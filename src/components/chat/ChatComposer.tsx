import { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';

export function ChatComposer() {
  const [message, setMessage] = useState('');
  const { toast } = useToast();

  const handleSend = () => {
    toast({
      title: 'Prototype Only',
      description: 'Chat functionality is not available in this prototype.',
    });
  };

  return (
    <div className="border-t border-border bg-card p-4">
      <div className="flex gap-2">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 bg-secondary"
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <Button onClick={handleSend} size="icon">
          <Send className="h-4 w-4" />
        </Button>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        Press Enter to send • This is a prototype
      </p>
    </div>
  );
}
