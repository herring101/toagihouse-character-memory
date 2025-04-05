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

// チャットAPIを呼び出す関数
export async function sendChatRequest(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(CHAT_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'APIリクエストに失敗しました');
  }

  return await response.json();
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
