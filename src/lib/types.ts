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

// =====================================================
// 기본 문제 (example_problem.json)
// =====================================================
export interface BaseProblem {
  id: string;
  original_id: string;
  name: string;
  question: string;
  input_output: { inputs: string[]; outputs: string[] };
  difficulty: Difficulty;
  tags: string[];
  source: string;
  url?: string;
  time_limit?: string;
  memory_limit?: string;
  solutions: Solution[];
}

export interface Solution {
  language: Framework;
  code: string;
}

// =====================================================
// 빈칸 채우기 (problems_blank.json)
// =====================================================
export interface BlankProblem {
  original_id: string;
  language: Framework;
  code_template: string;
  answers: string[];
}

// =====================================================
// 퍼즐 (problems_puzzle.json)
// =====================================================
export interface PuzzleBlock {
  id: number;
  code: string;
  indentation?: number;
}

export interface PuzzleProblem {
  original_id: string;
  language: Framework;
  fixed_start?: string;
  fixed_end?: string;
  blocks: PuzzleBlock[];
}

// =====================================================
// 1대1 대화형 (problems_guided.json)
// =====================================================
export interface GuidedProblem {
  original_id: string;
  language: Framework;
  concepts: string[];
  flow: string[];
  checkpoints: string[];
}

// =====================================================
// UI용 통합 Problem 인터페이스 (기존 호환)
// =====================================================
export interface Problem {
  id: string;
  original_id?: string;
  title: string;
  description: string;
  framework: Framework;
  difficulty: Difficulty;
  topics: string[];
  estimatedTime: number;
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

  // For puzzle type
  puzzleBlocks?: PuzzleBlock[];
  fixed_start?: string;
  fixed_end?: string;
  // For guided type
  guidedData?: GuidedProblemData;
  // For implementation type
  implementationData?: ImplementationProblemData;
}

// Guided step for AI tutor (UI용)
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
