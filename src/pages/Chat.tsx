import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { SearchResultPanel } from '@/components/chat/SearchResultPanel';

const Chat = () => {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />
      <TopNav />
      <div className="flex flex-1 gap-6 p-6">
        <div className="flex-1"><ChatPanel /></div>
        <div className="hidden w-[480px] lg:block"><SearchResultPanel /></div>
      </div>
    </div>
  );
};

export default Chat;
