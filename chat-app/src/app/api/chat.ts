// チャットAPIとの通信を担当するクライアント

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  messages: Message[];
  model?: string;
  stream?: boolean;
}

export interface ChatResponse {
  id: string;
  created: number;
  model: string;
  content: string;
  role: string;
}

export interface Model {
  id: string;
  name: string;
  provider: string;
}

export interface ModelsResponse {
  models: Model[];
}

// バックエンドAPIのURL
const BASE_URL = 'http://localhost:8000';
const CHAT_API_URL = `${BASE_URL}/api/chat`;
const MODELS_API_URL = `${BASE_URL}/api/models`;

// チャットAPIを呼び出す関数（非ストリーミング）
export async function sendChatRequest(request: ChatRequest): Promise<ChatResponse> {
  // ストリーミングを明示的に無効化
  const nonStreamingRequest = { ...request, stream: false };
  
  const response = await fetch(CHAT_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(nonStreamingRequest),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'APIリクエストに失敗しました');
  }

  return await response.json();
}

// ストリーミングAPIを呼び出す関数
export function sendStreamingChatRequest(
  request: ChatRequest, 
  onChunk: (chunk: string, done: boolean) => void,
  onError: (error: string) => void
): () => void {
  // ストリーミングを明示的に有効化
  const streamingRequest = { ...request, stream: true };
  
  const controller = new AbortController();
  const { signal } = controller;
  
  // 非同期処理を開始
  (async () => {
    try {
      const response = await fetch(CHAT_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(streamingRequest),
        signal,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'APIリクエストに失敗しました');
      }
      
      // Server-Sent Events (SSE) のレスポンスを処理
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('ストリーミングレスポンスの読み取りに失敗しました');
      }
      
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        // 受信したデータをデコード
        const text = decoder.decode(value, { stream: true });
        buffer += text;
        
        // SSEメッセージを処理
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                onError(data.error);
                return;
              }
              
              onChunk(data.content, data.done);
              
              if (data.done) {
                return;
              }
            } catch (e) {
              console.error('SSEメッセージの解析に失敗:', line, e);
            }
          }
        }
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name !== 'AbortError') {
        onError(error.message || 'ストリーミングに失敗しました');
      } else {
        onError('ストリーミングに失敗しました');
      }
    }
  })();
  
  // キャンセル関数を返す
  return () => controller.abort();
}

// 利用可能なモデル一覧を取得する関数
export async function getAvailableModels(): Promise<Model[]> {
  try {
    const response = await fetch(MODELS_API_URL);
    if (!response.ok) {
      throw new Error('モデル一覧の取得に失敗しました');
    }
    const data = await response.json() as ModelsResponse;
    return data.models;
  } catch (error) {
    console.error('Error fetching models:', error);
    return [];
  }
}
