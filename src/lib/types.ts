export interface User {
  id: string;
  username: string;
  email: string;
  avatarShape: 'hexagon' | 'circle' | 'diamond' | 'pentagon';
  avatarColor: string;
  level: number;
  currentXP: number;
  requiredXP: number;
  badges: Badge[];
  solvedCount: number;
  streak: number;
  joinedAt: string;
  subscription: 'free' | 'pro' | 'enterprise';
}

export interface Badge {
  id: string;
  name: string;
  icon: string;
  description: string;
  earnedAt: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface Problem {
  id: string;
  title: string;
  description: string;
  framework: Framework;
  difficulty: Difficulty;
  topics: string[];
  estimatedTime: number; // in minutes
  solvedCount: number;
  codeSnippet: string;
  blanks: Blank[];
  relatedDocs: RelatedDoc[];
  keyConcepts: string[];
}

export interface Blank {
  id: string;
  position: number;
  answer: string;
  hints: string[];
}

export interface RelatedDoc {
  title: string;
  url: string;
}

export type Framework = 'react' | 'vue' | 'angular' | 'svelte' | 'vanilla';
export type Difficulty = 'easy' | 'medium' | 'hard';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  chips?: QuickChip[];
}

export interface QuickChip {
  label: string;
  value: string;
  category: 'framework' | 'difficulty' | 'topic';
}

export interface ActivityDay {
  date: string;
  count: number;
  intensity: 0 | 1 | 2 | 3 | 4;
}

export interface RecentActivity {
  id: string;
  type: 'solved' | 'badge' | 'streak' | 'levelup';
  title: string;
  description: string;
  timestamp: string;
  xpGained?: number;
}
