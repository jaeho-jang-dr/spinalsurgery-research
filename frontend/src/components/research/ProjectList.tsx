'use client'

import { VscCircleFilled, VscLoading } from '../icons'

interface Project {
  id: string
  title: string
  field: string
  keywords: string[]
  description?: string
  status: string
  papers_count: number
  patients_count: number
  collaborators_count: number
  created_at: string
  updated_at: string
}

interface ProjectListProps {
  projects: Project[]
  selectedProject: string | null
  onSelectProject: (id: string) => void
  isLoading: boolean
}

export function ProjectList({ projects, selectedProject, onSelectProject, isLoading }: ProjectListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'text-vscode-text-dim'
      case 'in_progress': return 'text-vscode-blue'
      case 'completed': return 'text-vscode-green'
      default: return 'text-vscode-text-dim'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'draft': return '초안'
      case 'in_progress': return '진행중'
      case 'completed': return '완료'
      default: return status
    }
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <VscLoading className="animate-spin text-vscode-text-dim" size={24} />
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="text-center text-sm text-vscode-text-dim">
          <p>프로젝트가 없습니다.</p>
          <p className="mt-2">새 프로젝트를 시작해보세요!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {projects.map(project => (
        <div
          key={project.id}
          onClick={() => onSelectProject(project.id)}
          className={`p-3 border-b border-vscode-border cursor-pointer hover:bg-vscode-hover ${
            selectedProject === project.id ? 'bg-vscode-selection' : ''
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <VscCircleFilled size={8} className={getStatusColor(project.status)} />
                <h4 className="text-sm font-medium line-clamp-1">{project.title}</h4>
              </div>
              <div className="text-xs text-vscode-text-dim mb-1">
                {project.field} • {getStatusText(project.status)}
              </div>
              <div className="text-xs text-vscode-text-dim">
                논문 {project.papers_count}편 • 환자 {project.patients_count}명 • 연구자 {project.collaborators_count}명
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}