'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { PapersPanel } from '@/components/papers/PapersPanel'

export default function PapersPage() {
  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300">
      {/* VS Code 스타일 헤더 */}
      <header className="bg-[#2d2d30] border-b border-[#3e3e42] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-xl font-semibold text-white hover:text-gray-200">
              SpinalSurgery Research Platform
            </Link>
            <span className="text-sm text-gray-500">/ 논문</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link href="/research" className="hover:text-white transition-colors">연구</Link>
            <Link href="/papers" className="text-white">논문</Link>
            <Link href="/data" className="hover:text-white transition-colors">데이터</Link>
            <Link href="/ai" className="hover:text-white transition-colors">AI</Link>
            <Link href="/settings" className="hover:text-white transition-colors">설정</Link>
          </nav>
        </div>
      </header>

      <main className="flex h-[calc(100vh-60px)]">
        <PapersPanel />
      </main>
    </div>
  )
}