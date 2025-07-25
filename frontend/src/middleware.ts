import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 개발 중에는 인증을 일시적으로 비활성화
  return NextResponse.next()
  
  // TODO: 백엔드 연결 후 아래 코드 활성화
  /*
  const token = request.cookies.get('access_token')
  const isLoginPage = request.nextUrl.pathname === '/login'

  if (!token && !isLoginPage) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (token && isLoginPage) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
  */
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}