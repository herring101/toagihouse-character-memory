from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from litellm import completion, acompletion

# 環境変数のロード
load_dotenv()

app = FastAPI(title="Chat API with LiteLLM")

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# モデルの定義
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gemini/gemini-2.0-flash"  # デフォルトモデル
    stream: bool = False


class ChatResponse(BaseModel):
    id: str
    created: int
    model: str
    content: str
    role: str


@app.get("/")
def read_root():
    return {"message": "LiteLLM Chat API"}


@app.get("/api/models")
def get_models():
    # 利用可能なモデルの一覧を返す
    # 実際のアプリでは、より詳細なモデル情報を返すことも可能
    models = [
        {
            "id": "gemini/gemini-2.0-flash",
            "name": "Gemini 2.0 Flash",
            "provider": "Google",
        },
        {"id": "openai/gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
        {"id": "openai/gpt-4o-mini", "name": "GPT-4o mini", "provider": "OpenAI"},
        {
            "id": "anthropic/claude-3-7-sonnet-20250219",
            "name": "Claude 3.7 Sonnet",
            "provider": "Anthropic",
        },
        {
            "id": "anthropic/claude-3-5-haiku-20241022",
            "name": "Claude 3.5 Haiku",
            "provider": "Anthropic",
        },
    ]
    return {"models": models}


@app.post("/api/chat")
async def chat(request: ChatRequest = Body(...)):
    try:
        # メッセージの形式変換
        messages = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        # LiteLLMを使用して応答を生成
        response = completion(
            model=request.model, messages=messages, stream=request.stream
        )

        # レスポンスの整形
        if request.stream:
            # ストリーミングレスポンスの場合はそのまま返す
            return response
        else:
            # 通常のレスポンスの場合は必要な情報を抽出
            return {
                "id": response.id,
                "created": response.created,
                "model": response.model,
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
            }
    except ValueError as e:
        # 明示的なバリデーションエラー
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # デバッグ情報を含むエラーメッセージ
        error_message = f"Error with model {request.model}: {str(e)}"
        print(error_message)  # サーバーログに出力
        raise HTTPException(status_code=500, detail=error_message)


# サーバー起動コマンド
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
