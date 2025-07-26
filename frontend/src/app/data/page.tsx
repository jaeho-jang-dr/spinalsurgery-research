'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function DataPage() {
  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-300">
      {/* VS Code 스타일 헤더 */}
      <header className="bg-[#2d2d30] border-b border-[#3e3e42] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-xl font-semibold text-white hover:text-gray-200">
              SpinalSurgery Research Platform
            </Link>
            <span className="text-sm text-gray-500">/ 데이터</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link href="/research" className="hover:text-white transition-colors">연구</Link>
            <Link href="/papers" className="hover:text-white transition-colors">논문</Link>
            <Link href="/data" className="text-white">데이터</Link>
            <Link href="/ai" className="hover:text-white transition-colors">AI</Link>
            <Link href="/settings" className="hover:text-white transition-colors">설정</Link>
          </nav>
        </div>
      </header>

      <main className="p-8">
        <h1 className="text-2xl font-bold text-white mb-6">데이터 관리</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-[#252526] border border-[#3e3e42] rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-2">환자 데이터</h2>
            <p className="text-gray-400 mb-4">환자 정보 및 의료 기록 관리</p>
            <button className="text-[#007acc] hover:text-[#1a8cff]">데이터 보기 →</button>
          </div>
          
          <div className="bg-[#252526] border border-[#3e3e42] rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-2">통계 분석</h2>
            <p className="text-gray-400 mb-4">데이터 시각화 및 통계 분석</p>
            <button className="text-[#007acc] hover:text-[#1a8cff]">분석 시작 →</button>
          </div>
          
          <div className="bg-[#252526] border border-[#3e3e42] rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-2">데이터 가져오기</h2>
            <p className="text-gray-400 mb-4">CSV, Excel 파일 업로드</p>
            <button className="text-[#007acc] hover:text-[#1a8cff]">파일 업로드 →</button>
          </div>
        </div>
      </main>
    </div>
  )
}