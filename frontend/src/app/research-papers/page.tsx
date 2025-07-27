'use client'

import React, { useState, useEffect } from 'react'
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent,
  Chip,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Divider,
  Stack,
  Alert,
  CircularProgress
} from '@mui/material'
import { 
  Search as SearchIcon,
  FilterList as FilterIcon,
  Article as ArticleIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Close as CloseIcon
} from '@mui/icons-material'
import { api } from '@/lib/api'
import { ActivityBar } from '@/components/layout/ActivityBar'
import { Sidebar } from '@/components/layout/Sidebar'
import { ResearchPapersPanel } from '@/components/research-papers/ResearchPapersPanel'
import { ResearchPanel } from '@/components/research/ResearchPanel'
import { PapersPanel } from '@/components/papers/PapersPanel'
import { SourcesPanel } from '@/components/sources/SourcesPanel'
import { AIPanel } from '@/components/ai/AIPanel'

interface ResearchPaper {
  pmid: string
  title: string
  abstract: string
  authors: string[]
  journal: string
  year: string
  doi: string
  pmc_id: string | null
  has_full_text: boolean
  fusion_type: string
  keywords: string[]
  abstract_content?: string
  full_text_content?: string
}

export default function ResearchPapersPage() {
  const [papers, setPapers] = useState<ResearchPaper[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPaper, setSelectedPaper] = useState<ResearchPaper | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  const [activeView, setActiveView] = useState('research-papers')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFusionType, setSelectedFusionType] = useState('')
  const [selectedYear, setSelectedYear] = useState('')
  const [fusionTypes, setFusionTypes] = useState<string[]>([])
  const [years, setYears] = useState<string[]>([])

  useEffect(() => {
    fetchPapers()
    fetchFilterOptions()
  }, [searchQuery, selectedFusionType, selectedYear])

  const fetchPapers = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (searchQuery) params.append('search_query', searchQuery)
      if (selectedFusionType) params.append('fusion_type', selectedFusionType)
      if (selectedYear) params.append('year', selectedYear)
      
      const response = await api.get(`/research-papers/?${params}`)
      setPapers(response.data)
      setError(null)
    } catch (err) {
      setError('논문을 불러오는데 실패했습니다.')
      console.error('Error fetching papers:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchFilterOptions = async () => {
    try {
      const [fusionTypesRes, yearsRes] = await Promise.all([
        api.get('/research-papers/fusion-types/list'),
        api.get('/research-papers/years/list')
      ])
      setFusionTypes(fusionTypesRes.data)
      setYears(yearsRes.data)
    } catch (err) {
      console.error('Error fetching filter options:', err)
    }
  }

  const viewPaperDetails = async (paper: ResearchPaper) => {
    try {
      const response = await api.get(`/research-papers/${paper.pmid}`)
      setSelectedPaper(response.data)
      setViewDialogOpen(true)
    } catch (err) {
      console.error('Error fetching paper details:', err)
    }
  }

  const handleCloseDialog = () => {
    setViewDialogOpen(false)
    setSelectedPaper(null)
  }

  const renderContent = () => {
    switch (activeView) {
      case 'research':
        return <ResearchPanel />
      case 'papers':
        return <PapersPanel />
      case 'sources':
        return <SourcesPanel />
      case 'ai':
        return <AIPanel />
      case 'research-papers':
      default:
        return <ResearchPapersPanel />
    }
  }

  return (
    <div className="flex h-screen bg-vscode-bg overflow-hidden">
      {/* Activity Bar */}
      <ActivityBar 
        activeView={activeView} 
        onViewChange={setActiveView}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />
      
      {/* Sidebar */}
      {sidebarOpen && <Sidebar activeView={activeView} />}
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}