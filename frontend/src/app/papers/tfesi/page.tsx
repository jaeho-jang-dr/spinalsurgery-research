'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Box } from '@mui/material';

// 동적 import로 SSR 이슈 방지
const TFESIPapersViewer = dynamic(
  () => import('@/components/papers/TFESIPapersViewer'),
  { ssr: false }
);

export default function TFESIPapersPage() {
  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <TFESIPapersViewer />
    </Box>
  );
}