#!/bin/bash

echo "🔧 PostgreSQL과 Redis 로컬 설치 스크립트"
echo "========================================"

# 설치 디렉토리 설정
INSTALL_DIR="$HOME/local"
mkdir -p "$INSTALL_DIR/bin"
mkdir -p "$INSTALL_DIR/lib"
mkdir -p "$INSTALL_DIR/data"

# PostgreSQL Portable 다운로드 및 설치
install_postgresql() {
    echo "📦 PostgreSQL 설치 중..."
    
    # PostgreSQL 바이너리 다운로드 (Ubuntu용)
    cd /tmp
    wget -q https://get.enterprisedb.com/postgresql/postgresql-15.5-1-linux-x64-binaries.tar.gz
    
    if [ -f postgresql-15.5-1-linux-x64-binaries.tar.gz ]; then
        tar -xzf postgresql-15.5-1-linux-x64-binaries.tar.gz
        mv pgsql "$INSTALL_DIR/postgresql"
        
        # 환경 변수 설정
        echo "export PATH=$INSTALL_DIR/postgresql/bin:\$PATH" >> ~/.bashrc
        echo "export PGDATA=$INSTALL_DIR/data/postgresql" >> ~/.bashrc
        
        # 데이터베이스 초기화
        mkdir -p "$INSTALL_DIR/data/postgresql"
        "$INSTALL_DIR/postgresql/bin/initdb" -D "$INSTALL_DIR/data/postgresql"
        
        echo "✅ PostgreSQL 설치 완료!"
    else
        echo "❌ PostgreSQL 다운로드 실패"
    fi
}

# Redis 소스에서 컴파일 및 설치
install_redis() {
    echo "📦 Redis 설치 중..."
    
    cd /tmp
    wget -q http://download.redis.io/redis-stable.tar.gz
    
    if [ -f redis-stable.tar.gz ]; then
        tar xvzf redis-stable.tar.gz
        cd redis-stable
        
        # 컴파일
        make
        
        # 바이너리 복사
        cp src/redis-server "$INSTALL_DIR/bin/"
        cp src/redis-cli "$INSTALL_DIR/bin/"
        
        # 설정 파일 생성
        mkdir -p "$INSTALL_DIR/etc"
        cat > "$INSTALL_DIR/etc/redis.conf" << EOF
port 6379
dir $INSTALL_DIR/data/redis
dbfilename dump.rdb
appendonly yes
appendfilename "appendonly.aof"
EOF
        
        # 데이터 디렉토리 생성
        mkdir -p "$INSTALL_DIR/data/redis"
        
        # 환경 변수 설정
        echo "export PATH=$INSTALL_DIR/bin:\$PATH" >> ~/.bashrc
        
        echo "✅ Redis 설치 완료!"
    else
        echo "❌ Redis 다운로드 실패"
    fi
}

# Docker Compose로 설치하는 대안
install_with_docker_compose() {
    echo "🐳 Docker Compose를 사용한 설치..."
    
    cat > docker-compose.local.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: spinalsurgery_postgres_local
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: spinalsurgery_research
    ports:
      - "5432:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: spinalsurgery_redis_local
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  redis_data:
EOF

    echo "Docker Compose 파일이 생성되었습니다."
    echo "실행: docker compose -f docker-compose.local.yml up -d"
}

# 선택 메뉴
echo ""
echo "설치 방법을 선택하세요:"
echo "1) 로컬 바이너리 설치 (권장)"
echo "2) Docker Compose 사용"
echo "3) 수동 설치 명령어 출력"
read -p "선택 (1-3): " choice

case $choice in
    1)
        install_postgresql
        install_redis
        echo ""
        echo "🎉 설치 완료! 다음 명령어로 서비스를 시작하세요:"
        echo "PostgreSQL: $INSTALL_DIR/postgresql/bin/pg_ctl -D $INSTALL_DIR/data/postgresql start"
        echo "Redis: $INSTALL_DIR/bin/redis-server $INSTALL_DIR/etc/redis.conf"
        ;;
    2)
        install_with_docker_compose
        ;;
    3)
        echo ""
        echo "수동 설치 명령어:"
        echo "# PostgreSQL"
        echo "sudo apt-get update"
        echo "sudo apt-get install -y postgresql postgresql-contrib"
        echo ""
        echo "# Redis"
        echo "sudo apt-get install -y redis-server"
        echo ""
        echo "# 또는 snap을 사용한 설치"
        echo "sudo snap install redis"
        ;;
esac