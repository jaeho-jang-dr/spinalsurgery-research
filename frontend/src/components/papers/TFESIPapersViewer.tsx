'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@mui/material';
import { 
  Box, 
  Button, 
  Typography, 
  List, 
  ListItem, 
  ListItemText,
  Divider,
  Paper,
  Tabs,
  Tab,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  FileText,
  Folder,
  Search,
  Download,
  ChevronRight,
  Globe,
  FileCheck,
  Users,
  ClipboardList
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TFESIPaper {
  id: string;
  type: 'published' | 'proposed';
  title: string;
  title_en?: string;
  journal?: string;
  year?: string;
  pmid?: string;
  pmc_id?: string;
  folder: string;
}

interface PaperDetails {
  id: string;
  type: string;
  title?: string;
  metadata?: any;
  files: Record<string, string>;
}

export default function TFESIPapersViewer() {
  const [papers, setPapers] = useState<TFESIPaper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<TFESIPaper | null>(null);
  const [paperDetails, setPaperDetails] = useState<PaperDetails | null>(null);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [fileContent, setFileContent] = useState<string>('');
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<'ko' | 'en'>('ko');

  // 논문 목록 가져오기
  useEffect(() => {
    fetchPapers();
  }, []);

  const fetchPapers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/tfesi-papers/list');
      const data = await response.json();
      if (data.status === 'success') {
        setPapers(data.papers);
      }
    } catch (err) {
      setError('논문 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 논문 상세 정보 가져오기
  const fetchPaperDetails = async (paperId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/tfesi-papers/paper/${paperId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setPaperDetails(data.paper);
        // 첫 번째 파일 자동 선택
        const fileKeys = Object.keys(data.paper.files);
        if (fileKeys.length > 0) {
          setSelectedFile(fileKeys[0]);
          setFileContent(data.paper.files[fileKeys[0]]);
        }
      }
    } catch (err) {
      setError('논문 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 논문 선택 핸들러
  const handlePaperSelect = (paper: TFESIPaper) => {
    setSelectedPaper(paper);
    fetchPaperDetails(paper.id);
    setActiveTab(0);
  };

  // 파일 선택 핸들러
  const handleFileSelect = (fileName: string) => {
    setSelectedFile(fileName);
    if (paperDetails) {
      setFileContent(paperDetails.files[fileName]);
    }
  };

  // 파일 아이콘 가져오기
  const getFileIcon = (fileName: string) => {
    if (fileName.includes('consent') || fileName.includes('동의')) return <FileCheck size={18} />;
    if (fileName.includes('questionnaire') || fileName.includes('설문')) return <ClipboardList size={18} />;
    if (fileName.includes('protocol') || fileName.includes('계획')) return <FileText size={18} />;
    if (fileName.includes('korean') || fileName.includes('한국')) return <Globe size={18} />;
    return <FileText size={18} />;
  };

  // 논문 타입별 칩 색상
  const getChipColor = (type: string) => {
    return type === 'published' ? 'primary' : 'secondary';
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h5" gutterBottom>
          TFESI 논문 뷰어
        </Typography>
        <Typography variant="body2" color="text.secondary">
          초음파 유도 경추간공 경막외 주사 관련 논문 및 연구 계획
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* 왼쪽: 논문 목록 */}
        <Box sx={{ width: 350, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          {/* 검색 바 */}
          <Box sx={{ p: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="논문 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search size={18} />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          <Divider />

          {/* 논문 목록 */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {papers
                .filter(paper => 
                  paper.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                  (paper.journal && paper.journal.toLowerCase().includes(searchQuery.toLowerCase()))
                )
                .map((paper) => (
                  <ListItem
                    key={paper.id}
                    button
                    selected={selectedPaper?.id === paper.id}
                    onClick={() => handlePaperSelect(paper)}
                    sx={{ 
                      borderBottom: 1, 
                      borderColor: 'divider',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" sx={{ flex: 1 }}>
                            {paper.title}
                          </Typography>
                          <Chip 
                            label={paper.type === 'published' ? '게재' : '제안'} 
                            size="small"
                            color={getChipColor(paper.type)}
                          />
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {paper.journal && `${paper.journal} • `}
                          {paper.year && `${paper.year} • `}
                          {paper.pmid && `PMID: ${paper.pmid}`}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
            </List>
          )}
        </Box>

        {/* 오른쪽: 논문 내용 */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {selectedPaper && paperDetails ? (
            <>
              {/* 논문 헤더 */}
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">
                    {selectedPaper.title}
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Globe size={16} />}
                    onClick={() => setLanguage(language === 'ko' ? 'en' : 'ko')}
                  >
                    {language === 'ko' ? 'English' : '한국어'}
                  </Button>
                </Box>
                {selectedPaper.title_en && language === 'en' && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {selectedPaper.title_en}
                  </Typography>
                )}
              </Box>

              {/* 파일 탭 */}
              <Tabs
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                {Object.keys(paperDetails.files).map((fileName, index) => (
                  <Tab
                    key={fileName}
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getFileIcon(fileName)}
                        <span>{fileName}</span>
                      </Box>
                    }
                    onClick={() => handleFileSelect(fileName)}
                  />
                ))}
              </Tabs>

              {/* 파일 내용 */}
              <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
                {fileContent.startsWith('PDF file:') ? (
                  <Alert severity="info">
                    PDF 파일입니다. 다운로드하여 확인하세요: {fileContent}
                  </Alert>
                ) : (
                  <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {fileContent}
                    </ReactMarkdown>
                  </Paper>
                )}
              </Box>
            </>
          ) : (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100%',
              color: 'text.secondary'
            }}>
              {error ? (
                <Alert severity="error">{error}</Alert>
              ) : (
                <Typography>왼쪽에서 논문을 선택하세요</Typography>
              )}
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}