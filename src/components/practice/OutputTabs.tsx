import { useState } from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Terminal, Eye, AlertCircle } from 'lucide-react';

export function OutputTabs() {
  const [activeTab, setActiveTab] = useState('console');

  const mockConsoleOutput = [
    { type: 'log', content: '> Starting development server...', time: '10:23:01' },
    { type: 'log', content: '> Compiling...', time: '10:23:02' },
    { type: 'success', content: '✓ Compiled successfully in 234ms', time: '10:23:03' },
    { type: 'log', content: '> Running tests...', time: '10:23:04' },
    { type: 'warn', content: '⚠ useEffect dependency array is missing "page"', time: '10:23:04' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-border bg-card"
    >
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="border-b border-border px-4">
          <TabsList className="h-12 bg-transparent p-0">
            <TabsTrigger
              value="console"
              className="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
            >
              <Terminal className="h-4 w-4" />
              Console
            </TabsTrigger>
            <TabsTrigger
              value="preview"
              className="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
            >
              <Eye className="h-4 w-4" />
              Preview
            </TabsTrigger>
            <TabsTrigger
              value="errors"
              className="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
            >
              <AlertCircle className="h-4 w-4" />
              Errors
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="console" className="m-0 p-4">
          <div className="h-32 overflow-auto rounded-lg bg-code-bg p-3 font-mono text-xs">
            {mockConsoleOutput.map((line, i) => (
              <div key={i} className="flex gap-3">
                <span className="text-code-comment">{line.time}</span>
                <span
                  className={
                    line.type === 'success'
                      ? 'text-primary'
                      : line.type === 'warn'
                      ? 'text-warning'
                      : 'text-foreground'
                  }
                >
                  {line.content}
                </span>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="preview" className="m-0 p-4">
          <div className="flex h-32 items-center justify-center rounded-lg border-2 border-dashed border-border bg-secondary/50">
            <p className="text-sm text-muted-foreground">
              Preview will appear here after running code
            </p>
          </div>
        </TabsContent>

        <TabsContent value="errors" className="m-0 p-4">
          <div className="flex h-32 items-center justify-center rounded-lg bg-code-bg">
            <p className="text-sm text-muted-foreground">No errors detected</p>
          </div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
