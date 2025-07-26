'use client'

import { useState, useEffect, useRef } from 'react'
import { VscNewFile, VscFolder, VscSearch, VscChevronRight, VscChevronDown, VscFile, VscBook, VscLoading, VscDebugPause, VscDebugStart, VscClose } from '../icons'
import { ResearchForm } from './ResearchForm'
import { ProjectList } from './ProjectList'
import { useProjectStore } from '@/stores/useProjectStore'
import { toast } from 'react-hot-toast'
import { api } from '@/lib/api'

export function ResearchPanel() {
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [showNewProject, setShowNewProject] = useState(false)
  const [showResearchForm, setShowResearchForm] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchSessions, setSearchSessions] = useState<any[]>([])
  const [activeJobs, setActiveJobs] = useState<Map<string, any>>(new Map())
  const monitoringIntervals = useRef<Map<string, NodeJS.Timeout>>(new Map())
  
  const { projects, currentProject, fetchProjects, createProject, setCurrentProject, isLoading } = useProjectStore()

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  useEffect(() => {
    if (selectedProject && projects.length > 0) {
      const project = projects.find(p => p.id === selectedProject)
      if (project) {
        setCurrentProject(project)
        // 검색 세션 가져오기
        fetchSearchSessions(selectedProject)
      }
    }
  }, [selectedProject, projects, setCurrentProject])

  const fetchSearchSessions = async (projectId: string) => {
    try {
      const response = await api.getSearchSessions(projectId)
      setSearchSessions(response.data)
      
      // 활성 작업 확인 및 모니터링 시작
      response.data.forEach((session: any) => {
        if (session.job_status && ['pending', 'running', 'paused'].includes(session.job_status)) {
          startSearchMonitoring(session.id)
        }
      })
    } catch (error) {
      console.error('Failed to fetch search sessions:', error)
    }
  }

  const startSearchMonitoring = (jobId: string) => {
    // 이미 모니터링 중이면 스킵
    if (monitoringIntervals.current.has(jobId)) {
      return
    }

    const interval = setInterval(async () => {
      try {
        const response = await api.getSearchJob(jobId)
        const jobInfo = response.data
        
        // 활성 작업 상태 업데이트
        setActiveJobs(prev => new Map(prev).set(jobId, jobInfo))
        
        // 완료되었거나 실패한 경우 모니터링 중지
        if (['completed', 'failed', 'cancelled'].includes(jobInfo.status)) {
          stopSearchMonitoring(jobId)
          
          if (jobInfo.status === 'completed') {
            toast.success(`검색 완료! ${jobInfo.progress}개 논문을 찾았습니다`)
            // 검색 세션 새로고침
            if (selectedProject) {
              fetchSearchSessions(selectedProject)
            }
          } else if (jobInfo.status === 'failed') {
            toast.error(`검색 실패: ${jobInfo.error_message || '알 수 없는 오류'}`)
          }
        }
      } catch (error) {
        console.error('Failed to monitor search job:', error)
      }
    }, 2000) // 2초마다 상태 확인
    
    monitoringIntervals.current.set(jobId, interval)
  }

  const stopSearchMonitoring = (jobId: string) => {
    const interval = monitoringIntervals.current.get(jobId)
    if (interval) {
      clearInterval(interval)
      monitoringIntervals.current.delete(jobId)
    }
    
    // 활성 작업에서 제거
    setActiveJobs(prev => {
      const newMap = new Map(prev)
      newMap.delete(jobId)
      return newMap
    })
  }

  const handleSearchControl = async (jobId: string, action: 'pause' | 'resume' | 'cancel') => {
    try {
      switch (action) {
        case 'pause':
          await api.pauseSearchJob(jobId)
          toast.info('검색이 일시정지되었습니다')
          break
        case 'resume':
          await api.resumeSearchJob(jobId)
          toast.info('검색이 재개되었습니다')
          break
        case 'cancel':
          await api.cancelSearchJob(jobId)
          toast.info('검색이 취소되었습니다')
          stopSearchMonitoring(jobId)
          break
      }
      
      // 상태 즉시 업데이트
      const response = await api.getSearchJob(jobId)
      setActiveJobs(prev => new Map(prev).set(jobId, response.data))
    } catch (error) {
      console.error(`Failed to ${action} search:`, error)
      toast.error(`검색 ${action} 실패`)
    }
  }

  // 컴포넌트 언마운트 시 모든 모니터링 중지
  useEffect(() => {
    return () => {
      monitoringIntervals.current.forEach((interval) => {
        clearInterval(interval)
      })
    }
  }, [])

  const handleCreateProject = async (data: any) => {
    try {
      const newProject = await createProject({
        title: data.title || `새 ${data.field} 연구`,
        field: data.field,
        keywords: data.keywords,
        description: data.details
      })
      
      toast.success('프로젝트가 생성되었습니다')
      setShowNewProject(false)
      setSelectedProject(newProject.id)
      
      // Refresh project list
      fetchProjects()
      
      // AI 옵션에 따른 처리
      if (data.aiOption === 'search') {
        toast.info('논문 검색을 시작합니다...')
        
        try {
          // 검색 사이트 가져오기
          const sitesResponse = await api.getSearchSites()
          const sites = sitesResponse.data
          const defaultSiteIds = sites
            .filter((site: any) => ['pubmed', 'pmc'].includes(site.id))
            .map((site: any) => site.id)
          
          // 연구 시작 (논문 검색)
          const researchResponse = await api.startResearch(newProject.id, {
            ai_option: 'search',
            site_ids: defaultSiteIds,
            target_count: 100  // 100개 논문 목표
          })
          
          if (researchResponse.data.status === 'success') {
            const jobId = researchResponse.data.job_id
            toast.success('논문 검색이 시작되었습니다!')
            
            // 검색 상태 모니터링 시작
            startSearchMonitoring(jobId)
          }
        } catch (error: any) {
          console.error('Failed to start research:', error)
          console.error('Error response:', error.response?.data)
          console.error('Error status:', error.response?.status)
          
          if (error.response?.status === 401) {
            toast.error('인증이 필요합니다. 다시 로그인해주세요.')
          } else if (error.response?.status === 404) {
            toast.error('API 엔드포인트를 찾을 수 없습니다.')
          } else {
            toast.error(`논문 검색에 실패했습니다: ${error.response?.data?.detail || error.message}`)
          }
        }
      } else if (data.aiOption === 'complete') {
        toast.info('완전 자동 연구를 시작합니다...')
        
        try {
          // Start complete AI research workflow
          const researchResponse = await api.startCompleteResearch({
            title: data.title || `${data.field} Research Study`,
            type: 'Clinical Study',
            keywords: data.keywords,
            objectives: data.details,
            description: data.details
          })
          
          if (researchResponse.data.status === 'completed') {
            toast.success('연구 프로젝트가 성공적으로 생성되었습니다!')
            toast.info(`프로젝트 ID: ${researchResponse.data.project_id}`)
            
            // Show results summary
            const outputs = researchResponse.data.outputs
            toast.success(`${outputs.documents_collected}개의 문서를 수집하고 논문 초안을 작성했습니다!`)
          }
        } catch (error) {
          console.error('Failed to start complete research:', error)
          toast.error('완전 자동 연구에 실패했습니다')
        }
      } else {
        toast.info(`${data.aiOption} 기능은 준비 중입니다`)
      }
    } catch (error) {
      console.error('Failed to create project:', error)
      toast.error('프로젝트 생성에 실패했습니다')
    }
  }

  const handleStartResearch = async (data: any) => {
    if (!currentProject) return
    
    try {
      if (data.aiOption === 'search') {
        toast.info('논문 검색을 시작합니다...')
        
        // 검색 사이트 가져오기
        const sitesResponse = await api.getSearchSites()
        const sites = sitesResponse.data
        const defaultSiteIds = sites
          .filter((site: any) => ['pubmed', 'pmc'].includes(site.id))
          .map((site: any) => site.id)
        
        // 연구 시작 (논문 검색)
        const researchResponse = await api.startResearch(currentProject.id, {
          ai_option: 'search',
          site_ids: defaultSiteIds,
          target_count: 100  // 100개 논문 목표
        })
        
        if (researchResponse.data.status === 'success') {
          const jobId = researchResponse.data.job_id
          toast.success('논문 검색이 시작되었습니다!')
          
          // 검색 상태 모니터링 시작
          startSearchMonitoring(jobId)
          setShowResearchForm(false)
          
          // 검색 세션 새로고침
          fetchSearchSessions(currentProject.id)
        }
      } else if (data.aiOption === 'complete') {
        toast.info('완전 자동 연구를 시작합니다...')
        
        try {
          // Start complete AI research workflow
          const researchResponse = await api.startCompleteResearch({
            title: data.title || currentProject.title,
            type: 'Clinical Study',
            keywords: data.keywords || currentProject.keywords,
            objectives: data.details,
            description: data.details
          })
          
          if (researchResponse.data.status === 'completed') {
            toast.success('연구가 성공적으로 완료되었습니다!')
            toast.info(`프로젝트 ID: ${researchResponse.data.project_id}`)
            
            // Show results summary
            const outputs = researchResponse.data.outputs
            toast.success(`${outputs.documents_collected}개의 문서를 수집하고 논문 초안을 작성했습니다!`)
            
            setShowResearchForm(false)
          }
        } catch (error) {
          console.error('Failed to start complete research:', error)
          toast.error('완전 자동 연구에 실패했습니다')
        }
      } else {
        toast.info(`${data.aiOption} 기능은 준비 중입니다`)
      }
    } catch (error: any) {
      console.error('Failed to start research:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      
      if (error.response?.status === 401) {
        toast.error('인증이 필요합니다. 다시 로그인해주세요.')
      } else if (error.response?.status === 404) {
        toast.error('API 엔드포인트를 찾을 수 없습니다.')
      } else {
        toast.error(`논문 검색에 실패했습니다: ${error.response?.data?.detail || error.message}`)
      }
    }
  }

  const filteredProjects = projects.filter(project => 
    searchQuery === '' || 
    project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.field.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.keywords.some(k => k.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="flex h-full">
      {/* Projects List */}
      <div className="w-80 bg-vscode-sidebar border-r border-vscode-border">
        <div className="p-2 border-b border-vscode-border">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs uppercase font-semibold text-vscode-text-dim">연구 프로젝트</h3>
            <button 
              onClick={() => setShowNewProject(true)}
              className="p-1 hover:bg-vscode-hover rounded"
              title="새 프로젝트"
            >
              <VscNewFile size={16} />
            </button>
          </div>
          <div className="relative">
            <VscSearch className="absolute left-2 top-1/2 transform -translate-y-1/2 text-vscode-text-dim" size={14} />
            <input 
              type="text" 
              placeholder="프로젝트 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="vscode-input pl-7 text-xs"
            />
          </div>
        </div>
        
        <ProjectList 
          projects={filteredProjects}
          selectedProject={selectedProject}
          onSelectProject={setSelectedProject}
          isLoading={isLoading}
        />
      </div>
      
      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {showNewProject || !selectedProject ? (
          <div className="p-8">
            <h1 className="text-2xl font-bold mb-6">새 연구 프로젝트 시작</h1>
            <ResearchForm onSubmit={handleCreateProject} />
          </div>
        ) : showResearchForm ? (
          <div className="p-8">
            <h1 className="text-2xl font-bold mb-2">{currentProject?.title}</h1>
            <p className="text-sm text-vscode-text-dim mb-6">이 프로젝트에서 새로운 연구를 시작합니다</p>
            <ResearchForm 
              onSubmit={handleStartResearch}
              initialValues={{
                field: currentProject?.field,
                keywords: currentProject?.keywords
              }}
            />
            <button
              onClick={() => setShowResearchForm(false)}
              className="mt-4 text-sm text-vscode-text-dim hover:text-vscode-text"
            >
              ← 프로젝트 정보로 돌아가기
            </button>
          </div>
        ) : (
          <div className="p-8">
            {currentProject && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl">{currentProject.title}</h2>
                  {activeJobs.size === 0 && (
                    <button
                      onClick={() => setShowResearchForm(true)}
                      className="px-4 py-2 bg-vscode-blue text-white rounded hover:bg-vscode-blue-dark transition-colors"
                    >
                      연구 시작하기
                    </button>
                  )}
                </div>
                <div className="space-y-4">
                  <div>
                    <span className="text-sm text-vscode-text-dim">분야:</span>
                    <span className="ml-2">{currentProject.field}</span>
                  </div>
                  <div>
                    <span className="text-sm text-vscode-text-dim">키워드:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {currentProject.keywords.map((keyword, idx) => (
                        <span key={idx} className="px-2 py-1 bg-vscode-bg text-xs rounded border border-vscode-border">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-vscode-text-dim">상태:</span>
                    <span className="ml-2">{currentProject.status}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="bg-vscode-bg-light p-4 rounded border border-vscode-border">
                      <div className="text-2xl font-bold">{currentProject.papers_count}</div>
                      <div className="text-sm text-vscode-text-dim">논문</div>
                    </div>
                    <div className="bg-vscode-bg-light p-4 rounded border border-vscode-border">
                      <div className="text-2xl font-bold">{currentProject.patients_count}</div>
                      <div className="text-sm text-vscode-text-dim">환자</div>
                    </div>
                    <div className="bg-vscode-bg-light p-4 rounded border border-vscode-border">
                      <div className="text-2xl font-bold">{currentProject.collaborators_count}</div>
                      <div className="text-sm text-vscode-text-dim">공동연구자</div>
                    </div>
                  </div>
                  
                  {/* 활성 검색 작업 */}
                  {activeJobs.size > 0 && (
                    <div className="mt-6">
                      <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <VscLoading className="animate-spin" size={18} />
                        진행 중인 검색
                      </h3>
                      <div className="space-y-2">
                        {Array.from(activeJobs.values()).map((job: any) => (
                          <div key={job.id} className="bg-vscode-bg-light p-4 rounded border border-vscode-blue">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium">{job.search_query}</span>
                              <div className="flex items-center gap-2">
                                {job.status === 'running' && (
                                  <button
                                    onClick={() => handleSearchControl(job.id, 'pause')}
                                    className="p-1 hover:bg-vscode-hover rounded"
                                    title="일시정지"
                                  >
                                    <VscDebugPause size={16} />
                                  </button>
                                )}
                                {job.status === 'paused' && (
                                  <button
                                    onClick={() => handleSearchControl(job.id, 'resume')}
                                    className="p-1 hover:bg-vscode-hover rounded"
                                    title="재개"
                                  >
                                    <VscDebugStart size={16} />
                                  </button>
                                )}
                                <button
                                  onClick={() => handleSearchControl(job.id, 'cancel')}
                                  className="p-1 hover:bg-vscode-hover rounded text-vscode-red"
                                  title="취소"
                                >
                                  <VscClose size={16} />
                                </button>
                              </div>
                            </div>
                            <div className="relative w-full h-2 bg-vscode-bg rounded overflow-hidden">
                              <div
                                className="absolute h-full bg-vscode-blue transition-all duration-300"
                                style={{ width: `${(job.progress / job.total_expected) * 100}%` }}
                              />
                            </div>
                            <div className="text-xs text-vscode-text-dim mt-1">
                              {job.progress} / {job.total_expected} 논문 ({Math.round((job.progress / job.total_expected) * 100)}%)
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 검색 세션 */}
                  {searchSessions.length > 0 && (
                    <div className="mt-6">
                      <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <VscBook size={18} />
                        논문 검색 기록
                      </h3>
                      <div className="space-y-2">
                        {searchSessions.map((session: any) => {
                          const activeJob = activeJobs.get(session.id)
                          
                          return (
                            <div key={session.id} className="bg-vscode-bg-light p-4 rounded border border-vscode-border">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <VscFile size={14} className="text-vscode-text-dim" />
                                    <span className="text-sm font-medium">검색어: {session.search_query}</span>
                                  </div>
                                  <div className="text-xs text-vscode-text-dim">
                                    검색일: {new Date(session.started_at).toLocaleString('ko-KR')}
                                  </div>
                                  <div className="text-xs text-vscode-text-dim mt-1">
                                    결과: 총 {session.total_results || activeJob?.progress || 0}건 
                                    {session.status === 'completed' && `(Abstract: ${session.abstract_count}, Full-text: ${session.fulltext_count})`}
                                  </div>
                                  {session.result_file_path && (
                                    <div className="text-xs text-vscode-blue mt-1">
                                      저장 위치: {session.result_file_path}
                                    </div>
                                  )}
                                </div>
                                <div className="ml-4">
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    activeJob ? (
                                      activeJob.status === 'running' ? 'bg-vscode-blue text-white' :
                                      activeJob.status === 'paused' ? 'bg-vscode-yellow text-black' :
                                      'bg-vscode-text-dim text-white'
                                    ) : (
                                      session.status === 'completed' ? 'bg-vscode-green text-white' : 
                                      session.status === 'in_progress' ? 'bg-vscode-blue text-white' : 
                                      'bg-vscode-text-dim text-white'
                                    )
                                  }`}>
                                    {activeJob ? (
                                      activeJob.status === 'running' ? '검색중' :
                                      activeJob.status === 'paused' ? '일시정지' :
                                      activeJob.status
                                    ) : (
                                      session.status === 'completed' ? '완료' : 
                                      session.status === 'in_progress' ? '진행중' : '대기'
                                    )}
                                  </span>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}