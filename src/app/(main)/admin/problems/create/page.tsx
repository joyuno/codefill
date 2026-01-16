'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Code2,
  Puzzle,
  BookOpen,
  FileText,
  Plus,
  Trash2,
  GripVertical,
  Loader2,
  X,
} from 'lucide-react';
import Link from 'next/link';
import { adminApi } from '@/lib/api/admin';
import { toast } from 'sonner';
import {
  Select as SelectUI,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type ProblemType = 'base' | 'blank' | 'puzzle' | 'guided';

interface BlankItem {
  id: string;
  index: number; // 빈칸 인덱스 (0, 1, 2...)
  answer: string;
  context: string; // 빈칸 주변 코드 컨텍스트
  lineNumber: number; // 빈칸이 있는 라인 번호
}

// 빈칸 마커 파싱 함수 (시스템 표준: _N_ 형식)
// 예: _0_, _1_, _2_ 또는 레거시 ___ 형식 지원
function parseBlankPositions(codeTemplate: string): { index: number; context: string; lineNumber: number }[] {
  const blanks: { index: number; context: string; lineNumber: number }[] = [];
  const lines = codeTemplate.split('\n');

  // _N_ 패턴 (예: _0_, _1_, _10_) 또는 레거시 ___ 패턴
  const blankPattern = /_(\d+)_|___/g;
  let sequentialIndex = 0;

  lines.forEach((line, lineIndex) => {
    const regex = new RegExp(blankPattern.source, 'g');
    let match;

    while ((match = regex.exec(line)) !== null) {
      const marker = match[0];
      // 빈칸 인덱스: _N_ 이면 N, ___ 이면 순차
      const blankIndex = match[1] !== undefined ? parseInt(match[1], 10) : sequentialIndex++;

      // 빈칸 주변 컨텍스트 추출
      const start = Math.max(0, match.index - 20);
      const end = Math.min(line.length, match.index + marker.length + 20);
      let context = line.substring(start, end);

      if (start > 0) context = '...' + context;
      if (end < line.length) context = context + '...';

      // 마커를 하이라이트용 플레이스홀더로 변경
      context = context.replace(marker, '{{BLANK}}');

      blanks.push({
        index: blankIndex,
        context: context.trim(),
        lineNumber: lineIndex + 1,
      });
    }
  });

  // 인덱스 순으로 정렬
  return blanks.sort((a, b) => a.index - b.index);
}

interface PuzzleBlock {
  id: number;
  code: string;
}

interface VariableGuide {
  name: string;
  role: string;
  type: string;
  initial?: string;
}

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: '쉬움', color: 'text-emerald-400' },
  { value: 'medium', label: '보통', color: 'text-amber-400' },
  { value: 'hard', label: '어려움', color: 'text-rose-400' },
];

const LANGUAGE_OPTIONS = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
];

const TYPE_OPTIONS = [
  { value: 'base', label: '원본', icon: FileText, color: 'text-slate-300', bg: 'bg-slate-500/15 border-slate-500/30', desc: '새 문제 생성' },
  { value: 'blank', label: '빈칸', icon: Code2, color: 'text-blue-400', bg: 'bg-blue-500/15 border-blue-500/30', desc: '빈칸 채우기', needsOriginal: true },
  { value: 'puzzle', label: '퍼즐', icon: Puzzle, color: 'text-violet-400', bg: 'bg-violet-500/15 border-violet-500/30', desc: '코드 순서 배치', needsOriginal: true },
  { value: 'guided', label: '가이드', icon: BookOpen, color: 'text-emerald-400', bg: 'bg-emerald-500/15 border-emerald-500/30', desc: '단계별 안내', needsOriginal: true },
];

export default function AdminProblemCreatePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const typeParam = searchParams.get('type') as ProblemType | null;
  const originalIdParam = searchParams.get('originalId');

  const [problemType, setProblemType] = useState<ProblemType>(typeParam || 'base');
  const [loading, setLoading] = useState(false);

  // Edit mode state - 기존 변형이 있으면 수정 모드
  const [editMode, setEditMode] = useState<{
    blank: { id: string; language: string } | null;
    puzzle: { id: string; language: string } | null;
    guided: { id: string; language: string } | null;
  }>({ blank: null, puzzle: null, guided: null });

  // Base problem form
  const [baseForm, setBaseForm] = useState({
    original_id: '',
    name: '',
    question: '',
    difficulty: 'medium',
    tags: [] as string[],
    source: '',
    url: '',
    time_limit: '',
    memory_limit: '',
    solutions: [{ language: 'python', code: '' }],
  });
  const [tagInput, setTagInput] = useState('');

  // Blank problem form
  const [blankForm, setBlankForm] = useState({
    code_template: '',
    blanks: [] as BlankItem[],
  });
  const isInitialBlankLoad = useRef(false); // 초기 데이터 로드 플래그

  // 코드 템플릿 변경 시 빈칸 자동 동기화
  useEffect(() => {
    if (problemType !== 'blank') return;

    // 초기 로드 시에는 건너뜀 (기존 데이터 유지)
    if (isInitialBlankLoad.current) {
      isInitialBlankLoad.current = false;
      return;
    }

    const parsedBlanks = parseBlankPositions(blankForm.code_template);

    setBlankForm((prev) => {
      // 기존 정답 유지하면서 새로운 빈칸 구조에 맞춤
      const newBlanks = parsedBlanks.map((parsed) => {
        // 같은 인덱스의 기존 빈칸 찾기
        const existingBlank = prev.blanks.find(b => b.index === parsed.index);
        return {
          id: `blank-${parsed.index}`,
          index: parsed.index,
          answer: existingBlank?.answer || '',
          context: parsed.context,
          lineNumber: parsed.lineNumber,
        };
      });

      return { ...prev, blanks: newBlanks };
    });
  }, [blankForm.code_template, problemType]);

  // Puzzle problem form
  const [puzzleForm, setPuzzleForm] = useState({
    language: 'python',
    fixed_start: '',
    fixed_end: '',
    blocks: [] as PuzzleBlock[],
  });

  // Guided problem form
  const [guidedForm, setGuidedForm] = useState({
    language: 'python',
    concept_explanation: '',
    variables_guide: [] as VariableGuide[],
    approach_guide: '',
    starter_code: '',
  });

  // Fetch base problem and check existing variants
  useEffect(() => {
    if (originalIdParam && typeParam && typeParam !== 'base') {
      const fetchBaseProblem = async () => {
        try {
          const data = await adminApi.getProblemDetail(originalIdParam);
          const solutionCode = data.solutions?.[0]?.code || '';
          const solutionLang = data.solutions?.[0]?.language || 'python';

          setBaseForm({
            original_id: data.original_id,
            name: data.name,
            question: data.question,
            difficulty: data.difficulty,
            tags: data.tags || [],
            source: data.source || '',
            url: data.url || '',
            time_limit: data.time_limit || '',
            memory_limit: data.memory_limit || '',
            solutions: data.solutions || [{ language: 'python', code: '' }],
          });

          // 기존 변형 체크 및 수정 모드 설정
          const newEditMode = { blank: null as { id: string; language: string } | null, puzzle: null as { id: string; language: string } | null, guided: null as { id: string; language: string } | null };

          // 빈칸 변형 체크
          if (data.blanks && data.blanks.length > 0) {
            const existing = data.blanks[0];
            newEditMode.blank = { id: existing.id, language: existing.language };
            if (typeParam === 'blank') {
              const codeTemplate = existing.code_template || '';
              const parsedBlanks = parseBlankPositions(codeTemplate);
              const answers = existing.answers || [];

              // 초기 로드 플래그 설정 (useEffect가 덮어쓰지 않도록)
              isInitialBlankLoad.current = true;

              setBlankForm({
                code_template: codeTemplate,
                blanks: parsedBlanks.length > 0
                  ? parsedBlanks.map((parsed) => ({
                      id: `blank-${parsed.index}`,
                      index: parsed.index,
                      answer: answers[parsed.index] || '',
                      context: parsed.context,
                      lineNumber: parsed.lineNumber,
                    }))
                  : answers.map((ans, i) => ({
                      id: `blank-${i}`,
                      index: i,
                      answer: ans,
                      context: '',
                      lineNumber: 0,
                    })),
              });
            }
          } else if (typeParam === 'blank') {
            setBlankForm({ code_template: solutionCode, blanks: [] });
          }

          // 퍼즐 변형 체크
          if (data.puzzles && data.puzzles.length > 0) {
            const existing = data.puzzles[0];
            newEditMode.puzzle = { id: existing.id, language: existing.language };
            if (typeParam === 'puzzle') {
              setPuzzleForm({
                language: existing.language,
                fixed_start: existing.fixed_start || '',
                fixed_end: existing.fixed_end || '',
                blocks: (existing.blocks || []).map((b: { id: number; code: string }) => ({
                  id: b.id,
                  code: b.code,
                })),
              });
            }
          } else if (typeParam === 'puzzle') {
            const lines = solutionCode.split('\n').filter((l: string) => l.trim());
            setPuzzleForm({
              language: solutionLang,
              fixed_start: '',
              fixed_end: '',
              blocks: lines.map((line: string, i: number) => ({ id: i, code: line })),
            });
          }

          // 가이드 변형 체크
          if (data.guideds && data.guideds.length > 0) {
            const existing = data.guideds[0];
            newEditMode.guided = { id: existing.id, language: existing.language };
            if (typeParam === 'guided') {
              setGuidedForm({
                language: existing.language,
                concept_explanation: existing.concept_explanation || '',
                variables_guide: existing.variables_guide || [],
                approach_guide: existing.approach_guide || '',
                starter_code: existing.starter_code || '',
              });
            }
          } else if (typeParam === 'guided') {
            setGuidedForm({
              language: solutionLang,
              concept_explanation: '',
              variables_guide: [],
              approach_guide: '',
              starter_code: '',
            });
          }

          setEditMode(newEditMode);
        } catch (error) {
          console.error('Failed to fetch base problem:', error);
          toast.error('원본 문제를 불러오는데 실패했습니다');
        }
      };
      fetchBaseProblem();
    }
  }, [originalIdParam, typeParam]);

  // Handlers
  const handleCreateBase = async () => {
    if (!baseForm.original_id || !baseForm.name || !baseForm.question) {
      toast.error('필수 항목을 입력해주세요 (ID, 제목, 설명)');
      return;
    }
    if (!baseForm.solutions[0]?.code) {
      toast.error('솔루션 코드를 입력해주세요');
      return;
    }

    setLoading(true);
    try {
      const result = await adminApi.createBaseProblem({
        original_id: baseForm.original_id,
        name: baseForm.name,
        question: baseForm.question,
        difficulty: baseForm.difficulty,
        tags: baseForm.tags,
        source: baseForm.source || undefined,
        url: baseForm.url || undefined,
        time_limit: baseForm.time_limit || undefined,
        memory_limit: baseForm.memory_limit || undefined,
        solutions: baseForm.solutions.filter(s => s.code.trim()),
      });
      toast.success('문제가 생성되었습니다');
      router.push(`/admin/problems/${result.original_id}`);
    } catch (error) {
      console.error('Failed to create base problem:', error);
      toast.error('문제 생성 실패');
    } finally {
      setLoading(false);
    }
  };

  // 빈칸 인덱스에 맞게 정답 배열 생성
  const buildAnswersArray = (blanks: BlankItem[]): string[] => {
    if (blanks.length === 0) return [];
    const maxIndex = Math.max(...blanks.map(b => b.index));
    const answers = Array(maxIndex + 1).fill('');
    blanks.forEach(b => {
      answers[b.index] = b.answer;
    });
    return answers;
  };

  const handleCreateBlank = async () => {
    if (!originalIdParam || blankForm.blanks.length === 0) {
      toast.error('빈칸을 1개 이상 추가해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.createBlankProblem(originalIdParam, {
        language: baseForm.solutions?.[0]?.language || 'python',
        code_template: blankForm.code_template,
        answers: buildAnswersArray(blankForm.blanks),
      });
      toast.success('빈칸 문제가 생성되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to create blank problem:', error);
      toast.error('생성 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePuzzle = async () => {
    if (!originalIdParam || puzzleForm.blocks.length === 0) {
      toast.error('블록을 1개 이상 추가해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.createPuzzleProblem(originalIdParam, {
        language: puzzleForm.language,
        fixed_start: puzzleForm.fixed_start || undefined,
        fixed_end: puzzleForm.fixed_end || undefined,
        blocks: puzzleForm.blocks.map((b) => ({ id: b.id, code: b.code })),
      });
      toast.success('퍼즐 문제가 생성되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to create puzzle problem:', error);
      toast.error('생성 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGuided = async () => {
    if (!originalIdParam) {
      toast.error('원본 문제가 필요합니다');
      return;
    }
    if (!guidedForm.concept_explanation || !guidedForm.approach_guide || !guidedForm.starter_code) {
      toast.error('필수 항목을 입력해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.createGuidedProblem(originalIdParam, {
        language: guidedForm.language,
        concept_explanation: guidedForm.concept_explanation,
        variables_guide: guidedForm.variables_guide,
        approach_guide: guidedForm.approach_guide,
        starter_code: guidedForm.starter_code,
      });
      toast.success('가이드 문제가 생성되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to create guided problem:', error);
      toast.error('생성 실패');
    } finally {
      setLoading(false);
    }
  };

  // Update handlers
  const handleUpdateBlank = async () => {
    if (!originalIdParam || !editMode.blank) return;
    if (blankForm.blanks.length === 0) {
      toast.error('빈칸을 1개 이상 추가해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.updateBlankProblem(originalIdParam, editMode.blank.id, {
        code_template: blankForm.code_template,
        answers: buildAnswersArray(blankForm.blanks),
      });
      toast.success('빈칸 문제가 수정되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to update blank problem:', error);
      toast.error('수정 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePuzzle = async () => {
    if (!originalIdParam || !editMode.puzzle) return;
    if (puzzleForm.blocks.length === 0) {
      toast.error('블록을 1개 이상 추가해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.updatePuzzleProblem(originalIdParam, editMode.puzzle.id, {
        fixed_start: puzzleForm.fixed_start || undefined,
        fixed_end: puzzleForm.fixed_end || undefined,
        blocks: puzzleForm.blocks.map((b) => ({ id: b.id, code: b.code })),
      });
      toast.success('퍼즐 문제가 수정되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to update puzzle problem:', error);
      toast.error('수정 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateGuided = async () => {
    if (!originalIdParam || !editMode.guided) return;
    if (!guidedForm.concept_explanation || !guidedForm.approach_guide || !guidedForm.starter_code) {
      toast.error('필수 항목을 입력해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.updateGuidedProblem(originalIdParam, editMode.guided.id, {
        concept_explanation: guidedForm.concept_explanation,
        variables_guide: guidedForm.variables_guide,
        approach_guide: guidedForm.approach_guide,
        starter_code: guidedForm.starter_code,
      });
      toast.success('가이드 문제가 수정되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to update guided problem:', error);
      toast.error('수정 실패');
    } finally {
      setLoading(false);
    }
  };

  // Delete handlers
  const handleDeleteVariant = async (type: 'blank' | 'puzzle' | 'guided') => {
    if (!originalIdParam) return;
    const variantInfo = editMode[type];
    if (!variantInfo) return;

    if (!confirm('정말 삭제하시겠습니까?')) return;

    setLoading(true);
    try {
      if (type === 'blank') {
        await adminApi.deleteBlankProblem(originalIdParam, variantInfo.id);
      } else if (type === 'puzzle') {
        await adminApi.deletePuzzleProblem(originalIdParam, variantInfo.id);
      } else if (type === 'guided') {
        await adminApi.deleteGuidedProblem(originalIdParam, variantInfo.id);
      }
      toast.success('삭제되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to delete variant:', error);
      toast.error('삭제 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    switch (problemType) {
      case 'base': handleCreateBase(); break;
      case 'blank': editMode.blank ? handleUpdateBlank() : handleCreateBlank(); break;
      case 'puzzle': editMode.puzzle ? handleUpdatePuzzle() : handleCreatePuzzle(); break;
      case 'guided': editMode.guided ? handleUpdateGuided() : handleCreateGuided(); break;
    }
  };

  // 현재 타입의 수정 모드 여부
  const isEditMode = problemType === 'blank' ? !!editMode.blank
    : problemType === 'puzzle' ? !!editMode.puzzle
    : problemType === 'guided' ? !!editMode.guided
    : false;

  // Blank helpers (빈칸은 자동 감지되므로 add/remove 불필요)
  const updateBlank = (id: string, field: keyof BlankItem, value: string) => {
    setBlankForm({
      ...blankForm,
      blanks: blankForm.blanks.map((b) => (b.id === id ? { ...b, [field]: value } : b)),
    });
  };

  // Puzzle helpers
  const addPuzzleBlock = () => {
    const nextId = puzzleForm.blocks.length > 0 ? Math.max(...puzzleForm.blocks.map(b => b.id)) + 1 : 0;
    setPuzzleForm({ ...puzzleForm, blocks: [...puzzleForm.blocks, { id: nextId, code: '' }] });
  };

  const removePuzzleBlock = (id: number) => {
    setPuzzleForm({ ...puzzleForm, blocks: puzzleForm.blocks.filter((b) => b.id !== id) });
  };

  const updatePuzzleBlock = (id: number, value: string) => {
    setPuzzleForm({
      ...puzzleForm,
      blocks: puzzleForm.blocks.map((b) => (b.id === id ? { ...b, code: value } : b)),
    });
  };

  // Variable guide helpers
  const addVariableGuide = () => {
    setGuidedForm({
      ...guidedForm,
      variables_guide: [...guidedForm.variables_guide, { name: '', role: '', type: '', initial: '' }],
    });
  };

  const removeVariableGuide = (index: number) => {
    setGuidedForm({
      ...guidedForm,
      variables_guide: guidedForm.variables_guide.filter((_, i) => i !== index),
    });
  };

  const updateVariableGuide = (index: number, field: keyof VariableGuide, value: string) => {
    setGuidedForm({
      ...guidedForm,
      variables_guide: guidedForm.variables_guide.map((v, i) => (i === index ? { ...v, [field]: value } : v)),
    });
  };

  // Tag helpers
  const handleAddTag = () => {
    if (tagInput.trim() && !baseForm.tags.includes(tagInput.trim())) {
      setBaseForm({ ...baseForm, tags: [...baseForm.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setBaseForm({ ...baseForm, tags: baseForm.tags.filter((t) => t !== tag) });
  };

  // Input/Select components
  const Input = ({ label, required, ...props }: { label?: string; required?: boolean } & React.InputHTMLAttributes<HTMLInputElement>) => (
    <div className="space-y-1">
      {label && <label className="text-xs text-muted-foreground">{label}{required && ' *'}</label>}
      <input
        {...props}
        className={`w-full h-9 px-3 text-sm bg-white/5 border border-white/10 rounded-lg placeholder:text-muted-foreground/60 focus:outline-none focus:border-primary/50 transition-colors ${props.className || ''}`}
      />
    </div>
  );

  const TextArea = ({ label, required, rows = 4, ...props }: { label?: string; required?: boolean; rows?: number } & React.TextareaHTMLAttributes<HTMLTextAreaElement>) => (
    <div className="space-y-1">
      {label && <label className="text-xs text-muted-foreground">{label}{required && ' *'}</label>}
      <textarea
        rows={rows}
        {...props}
        className={`w-full px-3 py-2 text-sm bg-white/5 border border-white/10 rounded-lg placeholder:text-muted-foreground/60 focus:outline-none focus:border-primary/50 transition-colors resize-none ${props.className || ''}`}
      />
    </div>
  );

  const Select = ({ label, value, onChange, options }: { label?: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) => (
    <div className="space-y-1">
      {label && <label className="text-xs text-muted-foreground">{label}</label>}
      <SelectUI value={value} onValueChange={onChange}>
        <SelectTrigger className="w-full h-9 bg-white/5 border-white/10 rounded-lg">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
          ))}
        </SelectContent>
      </SelectUI>
    </div>
  );

  // Render forms
  const renderBaseForm = () => (
    <div className="space-y-6">
      {/* Row 1: ID, Title */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="문제 ID"
          required
          value={baseForm.original_id}
          onChange={(e) => setBaseForm({ ...baseForm, original_id: e.target.value })}
          placeholder="two-sum"
        />
        <Input
          label="제목"
          required
          value={baseForm.name}
          onChange={(e) => setBaseForm({ ...baseForm, name: e.target.value })}
          placeholder="Two Sum"
        />
      </div>

      {/* Row 2: Difficulty, Source, URL */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Select
          label="난이도"
          value={baseForm.difficulty}
          onChange={(v) => setBaseForm({ ...baseForm, difficulty: v })}
          options={DIFFICULTY_OPTIONS}
        />
        <Input
          label="출처"
          value={baseForm.source}
          onChange={(e) => setBaseForm({ ...baseForm, source: e.target.value })}
          placeholder="LeetCode"
        />
        <Input
          label="원본 URL"
          value={baseForm.url}
          onChange={(e) => setBaseForm({ ...baseForm, url: e.target.value })}
          placeholder="https://..."
        />
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">태그</label>
        <div className="flex gap-2">
          <input
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
            placeholder="Enter로 추가"
            className="flex-1 h-8 px-3 text-sm bg-white/5 border border-white/10 rounded-lg placeholder:text-muted-foreground/60 focus:outline-none focus:border-primary/50"
          />
        </div>
        {baseForm.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {baseForm.tags.map((tag) => (
              <span
                key={tag}
                onClick={() => handleRemoveTag(tag)}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-white/10 border border-white/10 rounded cursor-pointer hover:bg-white/15"
              >
                {tag}
                <X className="h-3 w-3" />
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Question */}
      <TextArea
        label="문제 설명"
        required
        value={baseForm.question}
        onChange={(e) => setBaseForm({ ...baseForm, question: e.target.value })}
        placeholder="문제 설명..."
        rows={5}
      />

      {/* Solutions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs text-muted-foreground">솔루션 *</label>
          <button
            type="button"
            onClick={() => setBaseForm({ ...baseForm, solutions: [...baseForm.solutions, { language: 'python', code: '' }] })}
            className="text-xs text-primary hover:underline"
          >
            + 솔루션 추가
          </button>
        </div>
        {baseForm.solutions.map((solution, index) => (
          <div key={index} className="space-y-2 p-3 bg-white/[0.07] border border-white/10 rounded-lg">
            <div className="flex items-center justify-between">
              <SelectUI
                value={solution.language}
                onValueChange={(val) => {
                  const newSolutions = [...baseForm.solutions];
                  newSolutions[index] = { ...newSolutions[index], language: val };
                  setBaseForm({ ...baseForm, solutions: newSolutions });
                }}
              >
                <SelectTrigger className="h-7 w-auto min-w-[100px] px-2 text-xs bg-white/5 border-white/10 rounded">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LANGUAGE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                  ))}
                </SelectContent>
              </SelectUI>
              {baseForm.solutions.length > 1 && (
                <button
                  type="button"
                  onClick={() => setBaseForm({ ...baseForm, solutions: baseForm.solutions.filter((_, i) => i !== index) })}
                  className="p-1 text-muted-foreground/60 hover:text-destructive"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
            <textarea
              value={solution.code}
              onChange={(e) => {
                const newSolutions = [...baseForm.solutions];
                newSolutions[index] = { ...newSolutions[index], code: e.target.value };
                setBaseForm({ ...baseForm, solutions: newSolutions });
              }}
              placeholder="솔루션 코드..."
              rows={8}
              className="w-full px-3 py-2 text-sm font-mono bg-black/20 border border-white/10 rounded placeholder:text-muted-foreground/60 focus:outline-none focus:border-primary/50 resize-none"
            />
          </div>
        ))}
      </div>

      {/* Time/Memory limits */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="시간 제한"
          value={baseForm.time_limit}
          onChange={(e) => setBaseForm({ ...baseForm, time_limit: e.target.value })}
          placeholder="1초"
        />
        <Input
          label="메모리 제한"
          value={baseForm.memory_limit}
          onChange={(e) => setBaseForm({ ...baseForm, memory_limit: e.target.value })}
          placeholder="256MB"
        />
      </div>
    </div>
  );

  const renderBlankForm = () => {
    const blankCount = blankForm.blanks.length;

    return (
      <div className="space-y-5">
        {/* 코드 템플릿 입력 */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground">
              코드 템플릿 <span className="text-primary/60">(_0_, _1_, _2_ 형식으로 빈칸 표시)</span>
            </label>
            {blankCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30">
                {blankCount}개 빈칸 감지됨
              </span>
            )}
          </div>
          <textarea
            value={blankForm.code_template}
            onChange={(e) => setBlankForm((prev) => ({ ...prev, code_template: e.target.value }))}
            placeholder={`def add(a, b):\n    result = _0_\n    return _1_`}
            rows={10}
            className="w-full px-3 py-2 text-sm font-mono bg-black/20 border border-white/10 rounded-lg placeholder:text-muted-foreground/40 focus:outline-none focus:border-primary/50 transition-colors resize-none"
          />
          <p className="text-[10px] text-muted-foreground/50">
            빈칸 형식: <code className="px-1 py-0.5 bg-white/10 rounded">_0_</code>, <code className="px-1 py-0.5 bg-white/10 rounded">_1_</code>, <code className="px-1 py-0.5 bg-white/10 rounded">_2_</code> ... (숫자 = 정답 배열 인덱스)
          </p>
        </div>

        {/* 빈칸 정답 입력 영역 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground">빈칸 정답</label>
            {blankCount === 0 && (
              <span className="text-xs text-muted-foreground/50">코드에 _0_, _1_ 형식을 입력하면 자동 감지됩니다</span>
            )}
          </div>

          <AnimatePresence mode="popLayout">
            {blankForm.blanks.length > 0 ? (
              <motion.div className="space-y-2">
                {blankForm.blanks.map((blank) => (
                  <motion.div
                    key={blank.id}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.15 }}
                    className="p-3 bg-white/[0.04] border border-white/10 rounded-lg hover:border-blue-500/30 transition-colors"
                  >
                    {/* 빈칸 헤더: 마커 + 라인 정보 */}
                    <div className="flex items-center gap-2 mb-2">
                      <code className="px-2 py-0.5 text-xs font-bold bg-blue-500/20 text-blue-400 rounded font-mono">
                        _{blank.index}_
                      </code>
                      {blank.lineNumber > 0 && (
                        <span className="text-[10px] text-muted-foreground/60">
                          Line {blank.lineNumber}
                        </span>
                      )}
                    </div>

                    {/* 코드 컨텍스트 표시 */}
                    {blank.lineNumber > 0 && blank.context && (
                      <div className="mb-3 px-3 py-2 bg-black/30 rounded-md border border-white/5">
                        <code className="text-xs text-muted-foreground font-mono">
                          {blank.context.split('{{BLANK}}').map((part, i, arr) => (
                            <span key={i}>
                              {part}
                              {i < arr.length - 1 && (
                                <span className="px-1.5 py-0.5 mx-0.5 bg-blue-500/30 text-blue-300 rounded font-bold">
                                  {blank.answer || `_${blank.index}_`}
                                </span>
                              )}
                            </span>
                          ))}
                        </code>
                      </div>
                    )}

                    {/* 정답 입력 */}
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground/60 shrink-0">정답:</span>
                      <input
                        value={blank.answer}
                        onChange={(e) => updateBlank(blank.id, 'answer', e.target.value)}
                        placeholder={`_${blank.index}_ 에 들어갈 정답`}
                        className="flex-1 h-8 px-3 text-sm font-mono bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-500/50 focus:bg-blue-500/5 transition-colors"
                      />
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="py-8 text-center border border-dashed border-white/10 rounded-lg"
              >
                <Code2 className="h-8 w-8 mx-auto mb-2 text-muted-foreground/30" />
                <p className="text-xs text-muted-foreground/50">
                  코드 템플릿에 <code className="px-1.5 py-0.5 bg-white/10 rounded text-blue-400">_0_</code>, <code className="px-1.5 py-0.5 bg-white/10 rounded text-blue-400">_1_</code> 형식을 입력하세요
                </p>
                <p className="text-[10px] text-muted-foreground/40 mt-1">
                  빈칸이 자동으로 감지됩니다
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 미리보기 영역 */}
        {blankForm.blanks.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs text-muted-foreground">미리보기</label>
            <div className="p-4 bg-black/30 border border-white/10 rounded-lg overflow-auto max-h-[200px]">
              <pre className="text-xs font-mono">
                {blankForm.code_template.split('\n').map((line, lineIndex) => {
                  // _N_ 패턴 또는 ___ 패턴 찾기
                  const blankPattern = /_(\d+)_|___/g;
                  const parts: React.ReactNode[] = [];
                  let lastIndex = 0;
                  let match;
                  let seqIndex = 0;

                  while ((match = blankPattern.exec(line)) !== null) {
                    // 매칭 전 텍스트
                    if (match.index > lastIndex) {
                      parts.push(
                        <span key={`t-${lineIndex}-${lastIndex}`}>{line.slice(lastIndex, match.index)}</span>
                      );
                    }

                    // 빈칸 인덱스 결정
                    const blankIndex = match[1] !== undefined ? parseInt(match[1], 10) : seqIndex++;
                    const blankData = blankForm.blanks.find(b => b.index === blankIndex);
                    const answer = blankData?.answer;

                    parts.push(
                      <span
                        key={`b-${lineIndex}-${match.index}`}
                        className={`px-1 py-0.5 rounded ${
                          answer
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        {answer || match[0]}
                      </span>
                    );

                    lastIndex = match.index + match[0].length;
                  }

                  // 남은 텍스트
                  if (lastIndex < line.length) {
                    parts.push(<span key={`t-${lineIndex}-end`}>{line.slice(lastIndex)}</span>);
                  }

                  return (
                    <div key={lineIndex} className="flex">
                      <span className="w-8 text-muted-foreground/40 select-none shrink-0">
                        {lineIndex + 1}
                      </span>
                      <span className="flex-1 whitespace-pre">{parts.length > 0 ? parts : line}</span>
                    </div>
                  );
                })}
              </pre>
            </div>
            <p className="text-[10px] text-muted-foreground/50">
              <span className="inline-block w-2 h-2 rounded-sm bg-emerald-500/30 mr-1" /> 정답 입력됨
              <span className="inline-block w-2 h-2 rounded-sm bg-rose-500/30 ml-3 mr-1" /> 정답 미입력
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderPuzzleForm = () => (
    <div className="space-y-5">
      <Select
        label="언어"
        value={puzzleForm.language}
        onChange={(v) => setPuzzleForm({ ...puzzleForm, language: v })}
        options={LANGUAGE_OPTIONS}
      />

      <TextArea
        label="고정 시작 코드 (선택)"
        value={puzzleForm.fixed_start}
        onChange={(e) => setPuzzleForm({ ...puzzleForm, fixed_start: e.target.value })}
        placeholder="블록 이전에 표시되는 코드"
        rows={2}
        className="font-mono"
      />

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs text-muted-foreground">코드 블록 (올바른 순서로)</label>
          <button type="button" onClick={addPuzzleBlock} className="text-xs text-primary hover:underline">+ 블록 추가</button>
        </div>

        <AnimatePresence>
          {puzzleForm.blocks.map((block, index) => (
            <motion.div
              key={block.id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-2"
            >
              <GripVertical className="h-4 w-4 text-muted-foreground/40" />
              <span className="flex items-center justify-center w-6 h-6 text-xs bg-white/10 rounded">{index + 1}</span>
              <input
                value={block.code}
                onChange={(e) => updatePuzzleBlock(block.id, e.target.value)}
                placeholder="코드 블록"
                className="flex-1 h-8 px-3 text-sm font-mono bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-primary/50"
              />
              <button onClick={() => removePuzzleBlock(block.id)} className="p-1.5 text-muted-foreground/60 hover:text-destructive">
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>

        {puzzleForm.blocks.length === 0 && (
          <div className="py-6 text-center text-xs text-muted-foreground/60 border border-dashed border-white/10 rounded-lg">
            블록을 추가하세요
          </div>
        )}
      </div>

      <TextArea
        label="고정 종료 코드 (선택)"
        value={puzzleForm.fixed_end}
        onChange={(e) => setPuzzleForm({ ...puzzleForm, fixed_end: e.target.value })}
        placeholder="블록 이후에 표시되는 코드"
        rows={2}
        className="font-mono"
      />
    </div>
  );

  const renderGuidedForm = () => (
    <div className="space-y-5">
      <Select
        label="언어"
        value={guidedForm.language}
        onChange={(v) => setGuidedForm({ ...guidedForm, language: v })}
        options={LANGUAGE_OPTIONS}
      />

      <TextArea
        label="개념 설명"
        required
        value={guidedForm.concept_explanation}
        onChange={(e) => setGuidedForm({ ...guidedForm, concept_explanation: e.target.value })}
        placeholder="이 문제에서 다루는 핵심 개념"
        rows={3}
      />

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs text-muted-foreground">변수 가이드</label>
          <button type="button" onClick={addVariableGuide} className="text-xs text-primary hover:underline">+ 변수 추가</button>
        </div>

        <AnimatePresence>
          {guidedForm.variables_guide.map((variable, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="p-3 space-y-2 bg-white/[0.07] border border-white/10 rounded-lg"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground/60">변수 {index + 1}</span>
                <button onClick={() => removeVariableGuide(index)} className="p-1 text-muted-foreground/60 hover:text-destructive">
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
              <div className="grid gap-2 sm:grid-cols-3">
                <input
                  value={variable.name}
                  onChange={(e) => updateVariableGuide(index, 'name', e.target.value)}
                  placeholder="이름"
                  className="h-8 px-2.5 text-sm bg-white/5 border border-white/10 rounded focus:outline-none focus:border-primary/50"
                />
                <input
                  value={variable.type}
                  onChange={(e) => updateVariableGuide(index, 'type', e.target.value)}
                  placeholder="타입"
                  className="h-8 px-2.5 text-sm bg-white/5 border border-white/10 rounded focus:outline-none focus:border-primary/50"
                />
                <input
                  value={variable.initial || ''}
                  onChange={(e) => updateVariableGuide(index, 'initial', e.target.value)}
                  placeholder="초기값"
                  className="h-8 px-2.5 text-sm bg-white/5 border border-white/10 rounded focus:outline-none focus:border-primary/50"
                />
              </div>
              <input
                value={variable.role}
                onChange={(e) => updateVariableGuide(index, 'role', e.target.value)}
                placeholder="역할 설명"
                className="w-full h-8 px-2.5 text-sm bg-white/5 border border-white/10 rounded focus:outline-none focus:border-primary/50"
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {guidedForm.variables_guide.length === 0 && (
          <div className="py-4 text-center text-xs text-muted-foreground/60 border border-dashed border-white/10 rounded-lg">
            변수 가이드 추가 (선택)
          </div>
        )}
      </div>

      <TextArea
        label="접근법"
        required
        value={guidedForm.approach_guide}
        onChange={(e) => setGuidedForm({ ...guidedForm, approach_guide: e.target.value })}
        placeholder="문제 해결 방법 단계별 설명"
        rows={5}
      />

      <TextArea
        label="시작 코드"
        required
        value={guidedForm.starter_code}
        onChange={(e) => setGuidedForm({ ...guidedForm, starter_code: e.target.value })}
        placeholder="학습자에게 제공할 초기 코드"
        rows={6}
        className="font-mono"
      />
    </div>
  );

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link
          href={originalIdParam ? `/admin/problems/${originalIdParam}` : '/admin/problems'}
          className="p-2 -ml-2 text-muted-foreground/60 hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div>
          <h1 className="text-lg font-semibold">
            {isEditMode ? '변형 수정' : '새 문제'}
          </h1>
          {originalIdParam && (
            <p className="text-xs text-muted-foreground/60">원본: {originalIdParam}</p>
          )}
        </div>
      </div>

      {/* Type Selection - Tab style */}
      <div className="flex gap-1 p-1 bg-white/[0.04] rounded-lg border border-white/10">
        {TYPE_OPTIONS.map((type) => {
          const Icon = type.icon;
          const isDisabled = type.needsOriginal && !originalIdParam;
          const isActive = problemType === type.value;
          // 해당 타입의 기존 변형 존재 여부
          const hasExisting = type.value === 'blank' ? !!editMode.blank
            : type.value === 'puzzle' ? !!editMode.puzzle
            : type.value === 'guided' ? !!editMode.guided
            : false;

          return (
            <button
              key={type.value}
              onClick={() => !isDisabled && setProblemType(type.value as ProblemType)}
              disabled={isDisabled}
              className={`relative flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-md text-sm font-medium transition-all border ${
                isActive
                  ? `${type.bg} ${type.color}`
                  : isDisabled
                    ? 'text-muted-foreground/40 cursor-not-allowed border-transparent'
                    : 'text-muted-foreground/70 hover:text-foreground hover:bg-white/[0.05] border-transparent'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{type.label}</span>
              {/* 기존 변형 있음 표시 */}
              {hasExisting && (
                <span className="absolute -top-1 -right-1 flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Form */}
      <div className="p-6 bg-white/[0.04] border border-white/10 rounded-xl">
        <AnimatePresence mode="wait">
          <motion.div
            key={problemType}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
          >
            {problemType === 'base' && renderBaseForm()}
            {problemType === 'blank' && renderBlankForm()}
            {problemType === 'puzzle' && renderPuzzleForm()}
            {problemType === 'guided' && renderGuidedForm()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Submit */}
      <div className="flex items-center justify-between">
        {/* 삭제 버튼 (수정 모드일 때만) */}
        {isEditMode && problemType !== 'base' && (
          <button
            onClick={() => handleDeleteVariant(problemType as 'blank' | 'puzzle' | 'guided')}
            disabled={loading}
            className="flex items-center gap-2 h-9 px-4 text-sm font-medium text-destructive bg-destructive/10 border border-destructive/20 rounded-lg hover:bg-destructive/20 disabled:opacity-50 transition-colors"
          >
            <Trash2 className="h-4 w-4" />
            삭제
          </button>
        )}
        {!isEditMode && <div />}

        {/* 생성/수정 버튼 */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="flex items-center gap-2 h-10 px-6 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          {loading
            ? (isEditMode ? '수정 중...' : '생성 중...')
            : (isEditMode ? '변형 수정' : '문제 생성')
          }
        </button>
      </div>
    </div>
  );
}
