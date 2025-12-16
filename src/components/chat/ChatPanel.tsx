import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatComposer } from './ChatComposer';
import { mockMessages } from '@/lib/mockData';
import { useToast } from '@/hooks/use-toast';

export function ChatPanel() {
  const { toast } = useToast();

  const handleChipClick = () => {
    toast({
      title: 'Prototype Only',
      description: 'Quick selection is not available in this prototype.',
    });
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-semibold">Practice Assistant</h3>
        <p className="text-xs text-muted-foreground">Tell me what you want to practice</p>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {mockMessages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onChipClick={handleChipClick}
            />
          ))}
        </div>
      </ScrollArea>

      <ChatComposer />
    </div>
  );
}
