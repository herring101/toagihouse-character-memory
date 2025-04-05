#!/bin/bash

# 色の設定
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== ToAGI House Character Memory アプリケーション起動 =====${NC}"

# バックエンドとフロントエンドを同時に起動する

# ターミナルを分割するためのファンクション
run_backend() {
  echo -e "${GREEN}バックエンドを起動しています...${NC}"
  cd "$(dirname "$0")/backend" && ./start.sh
}

run_frontend() {
  echo -e "${GREEN}フロントエンドを起動しています...${NC}"
  cd "$(dirname "$0")/chat-app" && npm run dev
}

# バックエンドをバックグラウンドで起動
run_backend & BACKEND_PID=$!

# 少し待ってからフロントエンドを起動（バックエンドが初期化される時間を確保）
sleep 2
run_frontend & FRONTEND_PID=$!

# どちらかのプロセスが終了したら両方を終了する
wait -n $BACKEND_PID $FRONTEND_PID
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null

echo -e "${BLUE}アプリケーションを終了しました${NC}"
