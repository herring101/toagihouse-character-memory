import { ChatInterface } from "@/components/chat/chat-interface";

export default function Home() {
  return (
    <main className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">LiteLLM Chat App</h1>
          <p className="text-muted-foreground">
            LiteLLMをバックエンドに、shadcn UIをフロントエンドに使用したチャットアプリケーション
          </p>
        </div>
        
        <ChatInterface />
        
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>バックエンドはPythonのLiteLLMを使用しています。フロントエンドはNext.js + shadcn UIで構築されています。</p>
        </div>
      </div>
    </main>
  );
}
