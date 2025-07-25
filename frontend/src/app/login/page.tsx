'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/useAuthStore'
import { VscAccount, VscLock, VscMail, VscPerson } from '../../components/icons'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const router = useRouter()
  const { login, register } = useAuthStore()
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    institution: '',
    department: '',
    role: 'researcher'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (isLogin) {
        await login(formData.email, formData.password)
        toast.success('로그인 성공!')
      } else {
        await register(formData)
        toast.success('회원가입 성공!')
      }
      router.push('/')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-vscode-bg flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-vscode-bg-light border border-vscode-border rounded-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mb-2">SpinalSurgery Research</h1>
            <p className="text-sm text-vscode-text-dim">
              {isLogin ? '계정에 로그인하세요' : '새 계정을 만드세요'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                <VscMail className="inline mr-1" size={16} />
                이메일
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="vscode-input w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                <VscLock className="inline mr-1" size={16} />
                비밀번호
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="vscode-input w-full"
                required
              />
            </div>

            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    <VscPerson className="inline mr-1" size={16} />
                    이름
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="vscode-input w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    기관
                  </label>
                  <input
                    type="text"
                    value={formData.institution}
                    onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
                    className="vscode-input w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    부서
                  </label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="vscode-input w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    역할
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="vscode-input w-full"
                  >
                    <option value="researcher">연구자</option>
                    <option value="admin">관리자</option>
                    <option value="viewer">열람자</option>
                  </select>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="vscode-button w-full py-2"
            >
              {loading ? '처리 중...' : (isLogin ? '로그인' : '회원가입')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-vscode-blue hover:underline"
            >
              {isLogin ? '계정이 없으신가요? 회원가입' : '이미 계정이 있으신가요? 로그인'}
            </button>
          </div>

          {isLogin && (
            <div className="mt-4 p-4 bg-vscode-bg rounded border border-vscode-border">
              <p className="text-xs text-vscode-text-dim mb-2">테스트 계정:</p>
              <p className="text-xs font-mono">Email: test@example.com</p>
              <p className="text-xs font-mono">Password: test1234</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}