import { User, Badge, Problem, Message, ActivityDay, RecentActivity } from './types';

export const mockUser: User = {
  id: '1',
  username: 'CodeNinja',
  email: 'ninja@code.dev',
  avatarShape: 'hexagon',
  avatarColor: 'hsl(142, 71%, 45%)',
  level: 23,
  currentXP: 2450,
  requiredXP: 3000,
  badges: [],
  solvedCount: 142,
  streak: 15,
  joinedAt: '2024-01-15',
  subscription: 'pro',
};

export const mockBadges: Badge[] = [
  { id: '1', name: 'First Steps', icon: '🎯', description: 'Complete your first problem', earnedAt: '2024-01-16', rarity: 'common' },
  { id: '2', name: 'Week Warrior', icon: '🔥', description: '7 day streak', earnedAt: '2024-02-01', rarity: 'common' },
  { id: '3', name: 'React Master', icon: '⚛️', description: 'Solve 50 React problems', earnedAt: '2024-03-15', rarity: 'rare' },
  { id: '4', name: 'Speed Demon', icon: '⚡', description: 'Solve 10 problems in one day', earnedAt: '2024-04-20', rarity: 'epic' },
  { id: '5', name: 'Perfectionist', icon: '💎', description: 'No hints on 25 problems', earnedAt: '2024-05-01', rarity: 'legendary' },
];

export const mockProblems: Problem[] = [
  {
    id: '1',
    title: 'React Infinite Scroll Implementation',
    description: 'Learn how to implement infinite scroll using React hooks and Intersection Observer API.',
    framework: 'react',
    difficulty: 'medium',
    topics: ['hooks', 'intersection-observer', 'performance'],
    estimatedTime: 25,
    solvedCount: 1234,
    codeSnippet: `import { useState, useEffect, useRef } from 'react';

function InfiniteScroll({ fetchMore }) {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const observerRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setPage(prev => prev + 1);
        }
      },
      { threshold: 0.1 }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    fetchMore(page).then(newItems => {
      setItems(prev => [...prev, ...newItems]);
    });
  }, [page, fetchMore]);

  return (
    <div>
      {items.map(item => <Item key={item.id} {...item} />)}
      <div ref={observerRef} />
    </div>
  );
}`,
    blanks: [
      { id: 'b1', position: 1, answer: 'useState', hints: ['React hook for state', 'Starts with "use"', 'useState'] },
      { id: 'b2', position: 2, answer: 'useEffect', hints: ['Side effects hook', 'Runs after render', 'useEffect'] },
      { id: 'b3', position: 3, answer: 'IntersectionObserver', hints: ['Browser API', 'Detects visibility', 'IntersectionObserver'] },
    ],
    relatedDocs: [
      { title: 'React Hooks Reference', url: 'https://react.dev/reference/react/hooks' },
      { title: 'MDN: Intersection Observer', url: 'https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API' },
    ],
    keyConcepts: ['useState', 'useEffect', 'useRef', 'Intersection Observer API'],
  },
  {
    id: '2',
    title: 'Vue Composition API Basics',
    description: 'Master the fundamentals of Vue 3 Composition API with reactive state.',
    framework: 'vue',
    difficulty: 'easy',
    topics: ['composition-api', 'reactive', 'ref'],
    estimatedTime: 15,
    solvedCount: 892,
    codeSnippet: `<script setup>
import { ref, computed } from 'vue';

const count = ref(0);
const doubled = computed(() => count.value * 2);

function increment() {
  count.value++;
}
</script>`,
    blanks: [
      { id: 'b1', position: 1, answer: 'ref', hints: ['Creates reactive reference', 'From vue', 'ref'] },
      { id: 'b2', position: 2, answer: 'computed', hints: ['Derived state', 'Cached value', 'computed'] },
    ],
    relatedDocs: [
      { title: 'Vue Composition API', url: 'https://vuejs.org/api/composition-api-setup.html' },
    ],
    keyConcepts: ['ref', 'computed', 'reactive', 'setup'],
  },
  {
    id: '3',
    title: 'Custom React Hook for API Calls',
    description: 'Build a reusable custom hook for fetching data with loading and error states.',
    framework: 'react',
    difficulty: 'hard',
    topics: ['custom-hooks', 'async', 'error-handling'],
    estimatedTime: 35,
    solvedCount: 567,
    codeSnippet: `function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const abortController = new AbortController();
    
    async function fetchData() {
      try {
        const response = await fetch(url, {
          signal: abortController.signal
        });
        const json = await response.json();
        setData(json);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(err);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    return () => abortController.abort();
  }, [url]);

  return { data, loading, error };
}`,
    blanks: [
      { id: 'b1', position: 1, answer: 'AbortController', hints: ['Cancellation API', 'Abort requests', 'AbortController'] },
      { id: 'b2', position: 2, answer: 'signal', hints: ['Abort property', 'Pass to fetch', 'signal'] },
      { id: 'b3', position: 3, answer: 'AbortError', hints: ['Error type', 'When aborted', 'AbortError'] },
    ],
    relatedDocs: [
      { title: 'Building Custom Hooks', url: 'https://react.dev/learn/reusing-logic-with-custom-hooks' },
      { title: 'MDN: AbortController', url: 'https://developer.mozilla.org/en-US/docs/Web/API/AbortController' },
    ],
    keyConcepts: ['Custom Hooks', 'AbortController', 'Error Boundaries', 'Cleanup'],
  },
  {
    id: '4',
    title: 'Angular Dependency Injection',
    description: 'Understand Angular services and dependency injection patterns.',
    framework: 'angular',
    difficulty: 'medium',
    topics: ['services', 'di', 'providers'],
    estimatedTime: 30,
    solvedCount: 423,
    codeSnippet: `@Injectable({
  providedIn: 'root'
})
export class DataService {
  constructor(private http: HttpClient) {}

  getData(): Observable<Data[]> {
    return this.http.get<Data[]>('/api/data');
  }
}`,
    blanks: [
      { id: 'b1', position: 1, answer: 'Injectable', hints: ['Decorator for DI', 'Makes it injectable', 'Injectable'] },
      { id: 'b2', position: 2, answer: 'providedIn', hints: ['Injection scope', 'Where to provide', 'providedIn'] },
    ],
    relatedDocs: [
      { title: 'Angular DI Guide', url: 'https://angular.io/guide/dependency-injection' },
    ],
    keyConcepts: ['Injectable', 'Providers', 'HttpClient', 'Observables'],
  },
  {
    id: '5',
    title: 'Svelte Reactive Statements',
    description: 'Learn Svelte reactive declarations and reactive statements.',
    framework: 'svelte',
    difficulty: 'easy',
    topics: ['reactive', 'stores', 'bindings'],
    estimatedTime: 20,
    solvedCount: 654,
    codeSnippet: `<script>
  let count = 0;
  $: doubled = count * 2;
  $: console.log(\`Count is \${count}\`);
</script>

<button on:click={() => count++}>
  Count: {count}, Doubled: {doubled}
</button>`,
    blanks: [
      { id: 'b1', position: 1, answer: '$:', hints: ['Reactive marker', 'Svelte syntax', '$:'] },
    ],
    relatedDocs: [
      { title: 'Svelte Reactivity', url: 'https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive' },
    ],
    keyConcepts: ['Reactive Declarations', 'Reactive Statements', 'Two-way Binding'],
  },
];

export const mockMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: "Hi! I'm here to help you practice coding. What would you like to work on today?",
    timestamp: '2024-06-01T10:00:00Z',
    chips: [
      { label: 'React', value: 'react', category: 'framework' },
      { label: 'Vue', value: 'vue', category: 'framework' },
      { label: 'Angular', value: 'angular', category: 'framework' },
    ],
  },
  {
    id: '2',
    role: 'user',
    content: "I want to practice React",
    timestamp: '2024-06-01T10:01:00Z',
  },
  {
    id: '3',
    role: 'assistant',
    content: "Great choice! React is popular. What difficulty level are you comfortable with?",
    timestamp: '2024-06-01T10:01:30Z',
    chips: [
      { label: 'Easy', value: 'easy', category: 'difficulty' },
      { label: 'Medium', value: 'medium', category: 'difficulty' },
      { label: 'Hard', value: 'hard', category: 'difficulty' },
    ],
  },
  {
    id: '4',
    role: 'user',
    content: "Medium difficulty sounds good",
    timestamp: '2024-06-01T10:02:00Z',
  },
  {
    id: '5',
    role: 'assistant',
    content: "Perfect! What topic interests you? Here are some popular ones:",
    timestamp: '2024-06-01T10:02:30Z',
    chips: [
      { label: 'Infinite Scroll', value: 'infinite-scroll', category: 'topic' },
      { label: 'Authentication', value: 'auth', category: 'topic' },
      { label: 'State Management', value: 'state', category: 'topic' },
    ],
  },
];

// Generate mock activity data for heatmap
export function generateMockActivityData(days: number = 365): ActivityDay[] {
  const data: ActivityDay[] = [];
  const today = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Random activity with some patterns
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const random = Math.random();
    
    let count = 0;
    let intensity: 0 | 1 | 2 | 3 | 4 = 0;
    
    if (random > (isWeekend ? 0.6 : 0.3)) {
      count = Math.floor(Math.random() * 10) + 1;
      intensity = count <= 2 ? 1 : count <= 4 ? 2 : count <= 7 ? 3 : 4;
    }
    
    data.push({
      date: date.toISOString().split('T')[0],
      count,
      intensity,
    });
  }
  
  return data;
}

export const mockRecentActivity: RecentActivity[] = [
  { id: '1', type: 'solved', title: 'Solved: React Infinite Scroll', description: 'Completed without hints', timestamp: '2024-06-01T09:30:00Z', xpGained: 150 },
  { id: '2', type: 'badge', title: 'New Badge: Speed Demon', description: 'Solved 10 problems in one day', timestamp: '2024-06-01T08:00:00Z' },
  { id: '3', type: 'streak', title: 'Streak Extended!', description: '15 days in a row', timestamp: '2024-05-31T23:59:00Z', xpGained: 50 },
  { id: '4', type: 'levelup', title: 'Level Up!', description: 'Reached Level 23', timestamp: '2024-05-30T15:00:00Z', xpGained: 500 },
  { id: '5', type: 'solved', title: 'Solved: Vue Composition API', description: 'Used 1 hint', timestamp: '2024-05-30T14:00:00Z', xpGained: 120 },
];

export const mockCodePreview = {
  title: 'React Infinite Scroll Implementation',
  description: 'This problem teaches you how to implement infinite scroll using the Intersection Observer API with React hooks. You\'ll learn to efficiently load content as users scroll.',
  code: `import { useState, useEffect, useRef } from 'react';

function InfiniteScroll({ fetchMore }) {
  const [items, setItems] = _____([]); // Blank 1
  const [page, setPage] = useState(1);
  const observerRef = useRef(null);

  _____(()  => { // Blank 2
    const observer = new _____(// Blank 3
      (entries) => {
        if (entries[0].isIntersecting) {
          setPage(prev => prev + 1);
        }
      },
      { threshold: 0.1 }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div>
      {items.map(item => <Item key={item.id} {...item} />)}
      <div ref={observerRef} />
    </div>
  );
}`,
};
