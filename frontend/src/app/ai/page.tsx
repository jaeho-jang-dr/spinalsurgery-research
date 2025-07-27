'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { AIPanel } from '@/components/ai/AIPanel'

export default function AIPage() {
  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300">
      {/* VS Code 스타일 헤더 */}
      <header className="bg-[#2d2d30] border-b border-[#3e3e42] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-xl font-semibold text-white hover:text-gray-200">
              SpinalSurgery Research Platform
            </Link>
            <span className="text-sm text-gray-500">/ AI 어시스턴트</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link href="/research" className="hover:text-white transition-colors">연구</Link>
            <Link href="/papers" className="hover:text-white transition-colors">논문</Link>
            <Link href="/research-papers" className="hover:text-white transition-colors">요추 유합술 논문</Link>
            <Link href="/data" className="hover:text-white transition-colors">데이터</Link>
            <Link href="/ai" className="text-white">AI</Link>
            <Link href="/settings" className="hover:text-white transition-colors">설정</Link>
          </nav>
        </div>
      </header>

      <main className="flex h-[calc(100vh-60px)]">
        <AIPanel />
      </main>
    </div>
  )
}