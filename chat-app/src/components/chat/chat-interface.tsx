"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChatMessage } from "./message";
import { Message, Model, sendChatRequest, sendStreamingChatRequest, getAvailableModels } from "@/app/api/chat";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "こんにちは！何かお手伝いできることはありますか？",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>("gemini/gemini-2.0-flash");
  const [availableModels, setAvailableModels] = useState<Model[]>([]);
  const [useStreaming, setUseStreaming] = useState<boolean>(true);
  const [streamingAbort, setStreamingAbort] = useState<(() => void) | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // 新しいメッセージが追加されたら自動スクロール
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  // 利用可能なモデル一覧を取得
  useEffect(() => {
    async function fetchModels() {
      const models = await getAvailableModels();
      setAvailableModels(models);
    }
    fetchModels();
  }, []);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // ユーザーメッセージを追加
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // ストリーミング中の場合は前回のストリーミングをキャンセル
    if (streamingAbort) {
      streamingAbort();
      setStreamingAbort(null);
    }

    // 新しいアシスタントメッセージを空の状態で追加（ストリーミング用）
    if (useStreaming) {
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    }

    try {
      if (useStreaming) {
        // ストリーミングAPIを使用
        const abort = sendStreamingChatRequest(
          {
            messages: [...messages, userMessage],
            model: selectedModel,
          },
          // チャンクを受け取るコールバック
          (chunk, done) => {
            if (done) {
              setIsLoading(false);
              setStreamingAbort(null);
            } else {
              // 最後のメッセージを更新（ストリーミング）
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                // 最後のメッセージがアシスタントのものであることを確認
                if (lastMessage.role === "assistant") {
                  newMessages[newMessages.length - 1] = {
                    ...lastMessage,
                    content: lastMessage.content + chunk,
                  };
                }
                return newMessages;
              });
            }
          },
          // エラーハンドリング
          (error) => {
            console.error("Error streaming message:", error);
            setMessages((prev) => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              // 最後のメッセージがアシスタントのものであることを確認
              if (lastMessage.role === "assistant") {
                newMessages[newMessages.length - 1] = {
                  ...lastMessage,
                  content: "申し訳ありません。エラーが発生しました。もう一度お試しください。",
                };
              }
              return newMessages;
            });
            setIsLoading(false);
          }
        );
        setStreamingAbort(() => abort);
      } else {
        // 通常のAPIリクエスト（非ストリーミング）
        const response = await sendChatRequest({
          messages: [...messages, userMessage],
          model: selectedModel,
        });

        // アシスタントの応答を追加
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: response.content },
        ]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "申し訳ありません。エラーが発生しました。もう一度お試しください。",
        },
      ]);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] max-w-3xl mx-auto border rounded-lg overflow-hidden">
      <div className="bg-primary p-3 text-primary-foreground flex justify-between items-center">
        <h2 className="text-xl font-bold">ToagiHouse AI Chat</h2>
        <div className="flex items-center space-x-3">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="streaming-toggle"
              checked={useStreaming}
              onChange={(e) => setUseStreaming(e.target.checked)}
              className="mr-1"
            />
            <label htmlFor="streaming-toggle" className="text-sm text-white cursor-pointer">
              ストリーミング
            </label>
          </div>
          <div className="flex items-center">
            <span className="mr-2 text-sm">モデル:</span>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-[180px] h-8 text-sm">
                <SelectValue placeholder="モデルを選択" />
              </SelectTrigger>
              <SelectContent>
                {availableModels.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name} ({model.provider})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
      
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="flex flex-col space-y-4">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-center my-2">
              <div className="animate-pulse text-muted-foreground">AI is thinking...</div>
            </div>
          )}
        </div>
      </ScrollArea>

      <Separator />
      
      <div className="p-4 flex gap-2">
        <Input
          placeholder="メッセージを入力..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !isLoading) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          disabled={isLoading}
          className="flex-1"
        />
        <Button 
          onClick={handleSendMessage} 
          disabled={isLoading || !input.trim()}
        >
          送信
        </Button>
      </div>
    </div>
  );
}
