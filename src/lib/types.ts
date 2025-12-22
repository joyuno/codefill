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

export type ProblemType = 'blank' | 'puzzle' | 'guided' | 'implementation';

export interface PuzzleBlock {
  id: string;
  code: string;
  indentation: number;
}

// Guided (1대1 대화형) problem types
export interface GuidedStep {
  stepNumber: number;
  aiMessage: string;
  responseType: 'text' | 'choice' | 'code';
  choices?: string[];
  correctChoice?: number;
  codeTemplate?: string;
  correctCode?: string;
  hint?: string;
}

export interface GuidedProblemData {
  steps: GuidedStep[];
  finalCode: string;
}

// Implementation problem types
export interface TestCase {
  input: any[];
  expected: any;
  isHidden?: boolean;
}

export interface ImplementationProblemData {
  functionSignature: string;
  testCases: TestCase[];
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
  problemType?: ProblemType;

  // Unified fields for all problem types (execution and testing)
  testCases?: TestCase[];         // Test cases for code execution
  solutionCode?: string;          // Correct solution code
  functionSignature?: string;     // Function signature for execution

  // For puzzle type (Parsons Problems)
  puzzleBlocks?: PuzzleBlock[];
  // For guided type (1대1 대화형)
  guidedData?: GuidedProblemData;
  // For implementation type (legacy - use testCases instead)
  implementationData?: ImplementationProblemData;
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

export type Framework = 'python' | 'java' | 'cpp' | 'javascript';
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
  category: 'framework' | 'difficulty' | 'topic' | 'action';
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
