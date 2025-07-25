import { create } from 'zustand'
import { api } from '@/lib/api'

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

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  isLoading: boolean
  fetchProjects: () => Promise<void>
  fetchProject: (id: string) => Promise<void>
  createProject: (data: any) => Promise<Project>
  updateProject: (id: string, data: any) => Promise<void>
  deleteProject: (id: string) => Promise<void>
  setCurrentProject: (project: Project | null) => void
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,
  isLoading: false,

  fetchProjects: async () => {
    set({ isLoading: true })
    try {
      const response = await api.getProjects()
      set({ projects: response.data })
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      set({ isLoading: false })
    }
  },

  fetchProject: async (id) => {
    set({ isLoading: true })
    try {
      const response = await api.getProject(id)
      set({ currentProject: response.data })
    } catch (error) {
      console.error('Failed to fetch project:', error)
    } finally {
      set({ isLoading: false })
    }
  },

  createProject: async (data) => {
    const response = await api.createProject(data)
    const newProject = response.data
    set((state) => ({ projects: [...state.projects, newProject] }))
    return newProject
  },

  updateProject: async (id, data) => {
    const response = await api.updateProject(id, data)
    const updatedProject = response.data
    set((state) => ({
      projects: state.projects.map((p) => (p.id === id ? updatedProject : p)),
      currentProject: state.currentProject?.id === id ? updatedProject : state.currentProject,
    }))
  },

  deleteProject: async (id) => {
    await api.deleteProject(id)
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
      currentProject: state.currentProject?.id === id ? null : state.currentProject,
    }))
  },

  setCurrentProject: (project) => {
    set({ currentProject: project })
  },
}))