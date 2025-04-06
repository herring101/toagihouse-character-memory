#!/bin/bash

# 色の設定
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== TOAGI House Character Memory 初期セットアップ =====${NC}"

# プロジェクトルートディレクトリの取得
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# .env.localの存在確認
if [ -f "$ROOT_DIR/.env.local" ]; then
  echo -e "${GREEN}.env.localファイルが見つかりました${NC}"
  set -a; source .env.local; set +a
fi

# フロントエンドのセットアップ
setup_frontend() {
  echo -e "${GREEN}フロントエンドの依存関係をインストールしています...${NC}"
  cd "$ROOT_DIR/chat-app" && npm install
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}フロントエンドのセットアップが完了しました${NC}"
  else
    echo -e "${YELLOW}フロントエンドのセットアップ中にエラーが発生しました${NC}"
    exit 1
  fi
}

# バックエンドのセットアップ
setup_backend() {
  echo -e "${GREEN}バックエンドの仮想環境を作成しています...${NC}"
  cd "$ROOT_DIR/backend"
  
  # 仮想環境の作成
  if [ ! -d "venv" ]; then
    python -m venv venv
  fi
  
  # 仮想環境のアクティベートと依存関係のインストール
  source venv/bin/activate
  pip install -r requirements.txt
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}バックエンドのセットアップが完了しました${NC}"
    deactivate
  else
    echo -e "${YELLOW}バックエンドのセットアップ中にエラーが発生しました${NC}"
    deactivate
    exit 1
  fi
}

# セットアップ関数の実行
setup_frontend
setup_backend

echo -e "${BLUE}===== セットアップが完了しました =====${NC}"
echo -e "${GREEN}アプリケーションを起動するには以下のコマンドを実行してください:${NC}"
echo -e "${YELLOW}./start-app.sh${NC}"
