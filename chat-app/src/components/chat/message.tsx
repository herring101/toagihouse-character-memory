import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Message } from "@/app/api/chat";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("flex gap-3 max-w-[80%]", isUser ? "flex-row-reverse" : "flex-row")}>
        <Avatar className="h-8 w-8">
          <AvatarFallback>{isUser ? "U" : "AI"}</AvatarFallback>
        </Avatar>

        <Card className={cn(
          "p-3 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}>
          <div className="whitespace-pre-wrap">{message.content}</div>
        </Card>
      </div>
    </div>
  );
}
