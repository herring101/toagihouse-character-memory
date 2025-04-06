import json
import os
from typing import AsyncIterator, Dict, List

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from litellm import completion
from pydantic import BaseModel

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

        # API キーのマッピング (Gemini API 用)
        if (
            "gemini" in request.model.lower()
            and os.environ.get("GOOGLE_API_KEY")
            and not os.environ.get("GEMINI_API_KEY")
        ):
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            if google_api_key:
                os.environ["GEMINI_API_KEY"] = google_api_key

        # ストリーミングレスポンスの場合
        if request.stream:
            return StreamingResponse(
                stream_response(request.model, messages), media_type="text/event-stream"
            )
        else:
            # 通常のレスポンスの場合
            response = completion(model=request.model, messages=messages, stream=False)

            # レスポンスの整形
            return {
                "id": response.id,
                "created": response.created,
                "model": response.model,
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
            }
    except ValueError as e:
        # 明示的なバリデーションエラー
        error_message = str(e)
        if "gemini" in request.model.lower() and "API key" in error_message:
            error_message = "Gemini API key is missing or invalid. Please check your GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        # デバッグ情報を含むエラーメッセージ
        error_message = f"Error with model {request.model}: {str(e)}"
        print(error_message)  # サーバーログに出力
        raise HTTPException(status_code=500, detail=error_message)


async def stream_response(
    model: str, messages: List[Dict[str, str]]
) -> AsyncIterator[str]:
    """
    ストリーミングレスポンスを生成するジェネレータ関数
    Server-Sent Events (SSE) 形式でレスポンスを返す
    """
    try:
        response = completion(model=model, messages=messages, stream=True)

        for chunk in response:
            if hasattr(chunk.choices[0], "delta"):
                # OpenAI互換フォーマット
                delta = chunk.choices[0].delta
                content = delta.content or ""

                # SSE形式でデータを返す
                if content:
                    yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
            else:
                # その他のフォーマット (必要に応じて調整)
                content = (
                    chunk.choices[0].message.content
                    if hasattr(chunk.choices[0], "message")
                    else ""
                )
                if content:
                    yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"

        # ストリーミング完了を示す最後のメッセージ
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
    except Exception as e:
        error_message = str(e)
        yield f"data: {json.dumps({'error': error_message, 'done': True})}\n\n"


# サーバー起動コマンド
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
