#!/bin/bash

# 色の設定
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== ToAGI House Character Memory 初期セットアップ =====${NC}"

# プロジェクトルートディレクトリの取得
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# .env.localのセットアップ
setup_env() {
  if [ ! -f "$ROOT_DIR/.env.local" ]; then
    echo -e "${GREEN}.env.localu30d5u30a1u30a4u30ebu3092u4f5cu6210u3057u307eu3059...${NC}"
    cat > "$ROOT_DIR/.env.local" << EOL
SUPABASE_DB_PASSWORD=
OPENAI_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=

EOL

    echo -e "${YELLOW}u6ce8u610f: .env.localu30d5u30a1u30a4u30ebu3092u4f5cu6210u3057u307eu3057u305fu3002APIu30adu30fcu3092u8a2du5b9au3057u3066u304fu3060u3055u3044u3002${NC}"
  else
    echo -e "${GREEN}.env.localu30d5u30a1u30a4u30ebu306fu65e2u306bu5b58u5728u3057u307eu3059${NC}"
  fi
}

# u30d5u30edu30f3u30c8u30a8u30f3u30c9u306eu30bbu30c3u30c8u30a2u30c3u30d7
setup_frontend() {
  echo -e "${GREEN}u30d5u30edu30f3u30c8u30a8u30f3u30c9u306eu4f9du5b58u95a2u4fc2u3092u30a4u30f3u30b9u30c8u30fcu30ebu3057u3066u3044u307eu3059...${NC}"
  cd "$ROOT_DIR/chat-app" && npm install
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}u30d5u30edu30f3u30c8u30a8u30f3u30c9u306eu30bbu30c3u30c8u30a2u30c3u30d7u304cu5b8cu4e86u3057u307eu3057u305f${NC}"
  else
    echo -e "${YELLOW}u30d5u30edu30f3u30c8u30a8u30f3u30c9u306eu30bbu30c3u30c8u30a2u30c3u30d7u4e2du306bu30a8u30e9u30fcu304cu767au751fu3057u307eu3057u305f${NC}"
    exit 1
  fi
}

# u30d0u30c3u30afu30a8u30f3u30c9u306eu30bbu30c3u30c8u30a2u30c3u30d7
setup_backend() {
  echo -e "${GREEN}u30d0u30c3u30afu30a8u30f3u30c9u306eu4eeeu60f3u74b0u5883u3092u4f5cu6210u3057u3066u3044u307eu3059...${NC}"
  cd "$ROOT_DIR/backend"
  
  # u4eeeu60f3u74b0u5883u306eu4f5cu6210
  if [ ! -d "venv" ]; then
    python -m venv venv
  fi
  
  # u4eeeu60f3u74b0u5883u306eu30a2u30afu30c6u30a3u30d9u30fcu30c8u3068u4f9du5b58u95a2u4fc2u306eu30a4u30f3u30b9u30c8u30fcu30eb
  source venv/bin/activate
  pip install -r requirements.txt
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}u30d0u30c3u30afu30a8u30f3u30c9u306eu30bbu30c3u30c8u30a2u30c3u30d7u304cu5b8cu4e86u3057u307eu3057u305f${NC}"
    deactivate
  else
    echo -e "${YELLOW}u30d0u30c3u30afu30a8u30f3u30c9u306eu30bbu30c3u30c8u30a2u30c3u30d7u4e2du306bu30a8u30e9u30fcu304cu767au751fu3057u307eu3057u305f${NC}"
    deactivate
    exit 1
  fi
}

# u30bbu30c3u30c8u30a2u30c3u30d7u95a2u6570u306eu5b9fu884c
setup_env
setup_frontend
setup_backend

echo -e "${BLUE}===== u30bbu30c3u30c8u30a2u30c3u30d7u304cu5b8cu4e86u3057u307eu3057u305f =====${NC}"
echo -e "${GREEN}u30a2u30d7u30eau30b1u30fcu30b7u30e7u30f3u3092u8d77u52d5u3059u308bu306bu306fu4ee5u4e0bu306eu30b3u30deu30f3u30c9u3092u5b9fu884cu3057u3066u304fu3060u3055u3044:${NC}"
echo -e "${YELLOW}./start-app.sh${NC}"

echo -e "${GREEN}u6ce8u610f: .env.localu30d5u30a1u30a4u30ebu306bAPIu30adu30fcu3092u8a2du5b9au3057u3066u3044u308bu3053u3068u3092u78bau8a8du3057u3066u304fu3060u3055u3044${NC}"
