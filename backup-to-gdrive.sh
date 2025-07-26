#!/bin/bash

# Google Drive 백업 스크립트
# 이 스크립트를 실행하여 프로젝트를 백업하고 Google Drive에 업로드할 준비를 합니다

echo "🔄 SpinalSurgery Research 프로젝트 백업 시작..."

# 백업 파일명 생성
BACKUP_NAME="spinalsurgery-research-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
BACKUP_PATH="/mnt/c/Users/DRJAY/Desktop/$BACKUP_NAME"

# 현재 디렉토리 저장
CURRENT_DIR=$(pwd)

# 상위 디렉토리로 이동하여 백업 생성
cd /home/drjang00/DevEnvironments

echo "📦 백업 파일 생성 중..."
tar -czf "$BACKUP_NAME" spinalsurgery-research/ \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.next' \
  --exclude='*.db' \
  --exclude='.git' \
  --exclude='*.log'

# Windows Desktop으로 복사
echo "📋 Windows Desktop으로 복사 중..."
cp "$BACKUP_NAME" "$BACKUP_PATH"

# 백업 파일 크기 확인
SIZE=$(ls -lh "$BACKUP_NAME" | awk '{print $5}')
echo "✅ 백업 완료! 파일 크기: $SIZE"

# 정리
rm "$BACKUP_NAME"

# 원래 디렉토리로 복귀
cd "$CURRENT_DIR"

echo ""
echo "📌 다음 단계:"
echo "1. Windows Desktop에서 '$BACKUP_NAME' 파일을 찾으세요"
echo "2. Google Drive (drive.google.com)에 로그인하세요"
echo "3. '새로 만들기' → '파일 업로드'를 선택하세요"
echo "4. Desktop에서 백업 파일을 선택하여 업로드하세요"
echo ""
echo "💡 새 컴퓨터에서 복원하려면:"
echo "   MIGRATION_GUIDE.md 파일을 참고하세요"