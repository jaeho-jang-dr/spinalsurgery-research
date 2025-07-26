'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function AnalysisPage() {
  const router = useRouter()

  useEffect(() => {
    // 데이터 분석 페이지로 리다이렉트
    router.push('/data')
  }, [router])

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300 flex items-center justify-center">
      <div>데이터 분석 페이지로 이동 중...</div>
    </div>
  )
}