import { PracticeHeader } from '@/components/practice/PracticeHeader';
import { PracticeDescription } from '@/components/practice/PracticeDescription';
import { EditorMock } from '@/components/practice/EditorMock';
import { OutputTabs } from '@/components/practice/OutputTabs';
import { mockProblems } from '@/lib/mockData';

const Practice = () => {
  const problem = mockProblems[0];
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <PracticeHeader title={problem.title} blanksFileld={3} totalBlanks={5} />
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-80 shrink-0 overflow-auto border-r border-border bg-card"><PracticeDescription problem={problem} /></aside>
        <main className="flex flex-1 flex-col">
          <div className="flex-1 p-4"><EditorMock problem={problem} /></div>
          <div className="border-t border-border p-4"><OutputTabs /></div>
        </main>
      </div>
    </div>
  );
};

export default Practice;
