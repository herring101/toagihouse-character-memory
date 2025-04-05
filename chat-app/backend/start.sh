#!/bin/bash

# 仮想環境のセットアップ（初回のみ）
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# 仮想環境のアクティベート
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# プロジェクトルートの.env.localファイルが存在する場合は読み込む
ROOT_ENV_FILE="../../.env.local"
if [ -f "$ROOT_ENV_FILE" ]; then
    echo "プロジェクトルートの.env.localファイルから環境変数を読み込みます"
    export $(grep -v '^#' $ROOT_ENV_FILE | xargs)
fi

# バックエンドディレクトリの.env.localファイルが存在する場合は読み込む
if [ -f ".env.local" ]; then
    echo "バックエンドディレクトリの.env.localファイルから環境変数を読み込みます"
    export $(grep -v '^#' .env.local | xargs)
fi

# 必要なAPIキーが設定されているか確認
if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "エラー: 少なくとも一つのAPIキーを設定してください。"
    echo "例:"
    echo "GEMINI_API_KEY=\"your-google-api-key\""
    echo "OPENAI_API_KEY=\"your-openai-api-key\""
    echo "ANTHROPIC_API_KEY=\"your-anthropic-api-key\""
    exit 1
fi

# サーバーの起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
