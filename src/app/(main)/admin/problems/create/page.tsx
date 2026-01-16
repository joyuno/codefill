'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Code2,
  Puzzle,
  BookOpen,
  FileText,
  Plus,
  Trash2,
  GripVertical,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { adminApi } from '@/lib/api/admin';
import { toast } from 'sonner';

type ProblemType = 'base' | 'blank' | 'puzzle' | 'guided';

interface BlankItem {
  id: string;
  answer: string;
  hint?: string;
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

const difficultyOptions = [
  { value: 'easy', label: '쉬움' },
  { value: 'medium', label: '보통' },
  { value: 'hard', label: '어려움' },
];

const languageOptions = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
];

export default function AdminProblemCreatePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const typeParam = searchParams.get('type') as ProblemType | null;
  const originalIdParam = searchParams.get('originalId');

  const [step, setStep] = useState(1);
  const [problemType, setProblemType] = useState<ProblemType>(typeParam || 'base');
  const [loading, setLoading] = useState(false);

  // Base problem form (백엔드 API 스키마에 맞춤)
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

  // Puzzle problem form (백엔드 API 스키마에 맞춤)
  const [puzzleForm, setPuzzleForm] = useState({
    language: 'python',
    fixed_start: '',
    fixed_end: '',
    blocks: [] as PuzzleBlock[],
  });

  // Guided problem form (DB 스키마에 맞춤)
  const [guidedForm, setGuidedForm] = useState({
    language: 'python',
    concept_explanation: '',
    variables_guide: [] as VariableGuide[],
    approach_guide: '',
    starter_code: '',
  });

  // If originalId is provided, fetch base problem details
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

          // Auto-generate initial data based on solution code
          if (typeParam === 'blank') {
            setBlankForm({
              code_template: solutionCode,
              blanks: [],
            });
          } else if (typeParam === 'puzzle') {
            const lines = solutionCode.split('\n').filter((l: string) => l.trim());
            setPuzzleForm({
              language: solutionLang,
              fixed_start: '',
              fixed_end: '',
              blocks: lines.map((line: string, i: number) => ({
                id: i,
                code: line,
              })),
            });
          } else if (typeParam === 'guided') {
            setGuidedForm({
              language: solutionLang,
              concept_explanation: '',
              variables_guide: [],
              approach_guide: '',
              starter_code: '',
            });
          }
          setStep(2);
        } catch (error) {
          console.error('Failed to fetch base problem:', error);
          toast.error('원본 문제를 불러오는데 실패했습니다');
        }
      };
      fetchBaseProblem();
    }
  }, [originalIdParam, typeParam]);

  const handleCreateBase = async () => {
    if (!baseForm.original_id || !baseForm.name || !baseForm.question) {
      toast.error('필수 항목을 모두 입력해주세요 (문제 ID, 제목, 설명)');
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
      toast.success('원본 문제가 생성되었습니다');
      router.push(`/admin/problems/${result.original_id}`);
    } catch (error) {
      console.error('Failed to create base problem:', error);
      toast.error('문제 생성에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBlank = async () => {
    if (!originalIdParam || blankForm.blanks.length === 0) {
      toast.error('빈칸을 최소 1개 이상 추가해주세요');
      return;
    }

    setLoading(true);
    try {
      const solutionLang = baseForm.solutions?.[0]?.language || 'python';
      await adminApi.createBlankProblem(originalIdParam, {
        language: solutionLang,
        code_template: blankForm.code_template,
        answers: blankForm.blanks.map((b) => b.answer),
      });
      toast.success('빈칸 채우기 문제가 생성되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to create blank problem:', error);
      toast.error('문제 생성에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePuzzle = async () => {
    if (!originalIdParam || puzzleForm.blocks.length === 0) {
      toast.error('블록을 최소 1개 이상 추가해주세요');
      return;
    }

    setLoading(true);
    try {
      await adminApi.createPuzzleProblem(originalIdParam, {
        language: puzzleForm.language,
        fixed_start: puzzleForm.fixed_start || undefined,
        fixed_end: puzzleForm.fixed_end || undefined,
        blocks: puzzleForm.blocks.map((b) => ({
          id: b.id,
          code: b.code,
        })),
      });
      toast.success('퍼즐 문제가 생성되었습니다');
      router.push(`/admin/problems/${originalIdParam}`);
    } catch (error) {
      console.error('Failed to create puzzle problem:', error);
      toast.error('문제 생성에 실패했습니다');
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
      toast.error('필수 항목을 모두 입력해주세요 (개념 설명, 접근법, 시작 코드)');
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
      toast.error('문제 생성에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const addBlank = () => {
    setBlankForm({
      ...blankForm,
      blanks: [
        ...blankForm.blanks,
        { id: `blank-${Date.now()}`, answer: '', hint: '' },
      ],
    });
  };

  const removeBlank = (id: string) => {
    setBlankForm({
      ...blankForm,
      blanks: blankForm.blanks.filter((b) => b.id !== id),
    });
  };

  const updateBlank = (id: string, field: keyof BlankItem, value: string) => {
    setBlankForm({
      ...blankForm,
      blanks: blankForm.blanks.map((b) =>
        b.id === id ? { ...b, [field]: value } : b
      ),
    });
  };

  const addPuzzleBlock = () => {
    const nextId = puzzleForm.blocks.length > 0
      ? Math.max(...puzzleForm.blocks.map(b => b.id)) + 1
      : 0;
    setPuzzleForm({
      ...puzzleForm,
      blocks: [
        ...puzzleForm.blocks,
        {
          id: nextId,
          code: '',
        },
      ],
    });
  };

  const removePuzzleBlock = (id: number) => {
    setPuzzleForm({
      ...puzzleForm,
      blocks: puzzleForm.blocks.filter((b) => b.id !== id),
    });
  };

  const updatePuzzleBlock = (
    id: number,
    field: keyof PuzzleBlock,
    value: string | number
  ) => {
    setPuzzleForm({
      ...puzzleForm,
      blocks: puzzleForm.blocks.map((b) =>
        b.id === id ? { ...b, [field]: value } : b
      ),
    });
  };

  // Variable guide functions for guided problems
  const addVariableGuide = () => {
    setGuidedForm({
      ...guidedForm,
      variables_guide: [
        ...guidedForm.variables_guide,
        {
          name: '',
          role: '',
          type: '',
          initial: '',
        },
      ],
    });
  };

  const removeVariableGuide = (index: number) => {
    setGuidedForm({
      ...guidedForm,
      variables_guide: guidedForm.variables_guide.filter((_, i) => i !== index),
    });
  };

  const updateVariableGuide = (
    index: number,
    field: keyof VariableGuide,
    value: string
  ) => {
    setGuidedForm({
      ...guidedForm,
      variables_guide: guidedForm.variables_guide.map((v, i) =>
        i === index ? { ...v, [field]: value } : v
      ),
    });
  };

  const renderTypeSelection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">문제 유형 선택</h2>
        <p className="text-muted-foreground">생성할 문제의 유형을 선택하세요</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card
          className={`cursor-pointer transition-all ${
            problemType === 'base'
              ? 'ring-2 ring-primary'
              : 'hover:border-primary/50'
          }`}
          onClick={() => setProblemType('base')}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-gray-500" />
              원본 문제
            </CardTitle>
            <CardDescription>
              새로운 코딩 문제를 처음부터 생성합니다
            </CardDescription>
          </CardHeader>
        </Card>

        <Card
          className={`cursor-pointer transition-all ${
            problemType === 'blank'
              ? 'ring-2 ring-primary'
              : 'hover:border-primary/50'
          } ${!originalIdParam && 'opacity-50 cursor-not-allowed'}`}
          onClick={() => originalIdParam && setProblemType('blank')}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-5 w-5 text-blue-500" />
              빈칸 채우기
              {!originalIdParam && (
                <Badge variant="outline" className="ml-auto">
                  원본 필요
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              코드의 일부를 빈칸으로 만들어 채우는 문제
            </CardDescription>
          </CardHeader>
        </Card>

        <Card
          className={`cursor-pointer transition-all ${
            problemType === 'puzzle'
              ? 'ring-2 ring-primary'
              : 'hover:border-primary/50'
          } ${!originalIdParam && 'opacity-50 cursor-not-allowed'}`}
          onClick={() => originalIdParam && setProblemType('puzzle')}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Puzzle className="h-5 w-5 text-purple-500" />
              퍼즐
              {!originalIdParam && (
                <Badge variant="outline" className="ml-auto">
                  원본 필요
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              코드 블록을 올바른 순서로 배치하는 문제
            </CardDescription>
          </CardHeader>
        </Card>

        <Card
          className={`cursor-pointer transition-all ${
            problemType === 'guided'
              ? 'ring-2 ring-primary'
              : 'hover:border-primary/50'
          } ${!originalIdParam && 'opacity-50 cursor-not-allowed'}`}
          onClick={() => originalIdParam && setProblemType('guided')}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-green-500" />
              가이드
              {!originalIdParam && (
                <Badge variant="outline" className="ml-auto">
                  원본 필요
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              단계별 안내와 함께 문제를 해결하는 문제
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  );

  const handleAddTag = () => {
    if (tagInput.trim() && !baseForm.tags.includes(tagInput.trim())) {
      setBaseForm({
        ...baseForm,
        tags: [...baseForm.tags, tagInput.trim()],
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setBaseForm({
      ...baseForm,
      tags: baseForm.tags.filter((t) => t !== tag),
    });
  };

  const renderBaseForm = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">원본 문제 생성</h2>
        <p className="text-muted-foreground">문제의 기본 정보를 입력하세요</p>
      </div>

      <div className="space-y-4">
        {/* 문제 ID와 제목 */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">문제 ID *</label>
            <Input
              value={baseForm.original_id}
              onChange={(e) => setBaseForm({ ...baseForm, original_id: e.target.value })}
              placeholder="예: two-sum, binary-search"
            />
            <p className="text-xs text-muted-foreground">영문, 숫자, 하이픈만 사용</p>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">제목 *</label>
            <Input
              value={baseForm.name}
              onChange={(e) => setBaseForm({ ...baseForm, name: e.target.value })}
              placeholder="문제 제목"
            />
          </div>
        </div>

        {/* 난이도와 출처 */}
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <label className="text-sm font-medium">난이도</label>
            <Select
              value={baseForm.difficulty}
              onValueChange={(v) => setBaseForm({ ...baseForm, difficulty: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {difficultyOptions.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">출처</label>
            <Input
              value={baseForm.source}
              onChange={(e) => setBaseForm({ ...baseForm, source: e.target.value })}
              placeholder="예: LeetCode, BOJ"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">원본 URL</label>
            <Input
              value={baseForm.url}
              onChange={(e) => setBaseForm({ ...baseForm, url: e.target.value })}
              placeholder="https://..."
            />
          </div>
        </div>

        {/* 태그 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">태그</label>
          <div className="flex gap-2">
            <Input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              placeholder="태그 입력 후 Enter"
              className="flex-1"
            />
            <Button type="button" variant="outline" onClick={handleAddTag}>
              추가
            </Button>
          </div>
          {baseForm.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {baseForm.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => handleRemoveTag(tag)}>
                  {tag} ×
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* 문제 설명 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">문제 설명 *</label>
          <Textarea
            value={baseForm.question}
            onChange={(e) => setBaseForm({ ...baseForm, question: e.target.value })}
            placeholder="문제에 대한 설명을 입력하세요"
            rows={6}
          />
        </div>

        {/* 솔루션 */}
        <div className="space-y-3">
          <label className="text-sm font-medium">솔루션 *</label>
          {baseForm.solutions.map((solution, index) => (
            <div key={index} className="space-y-2 p-4 border rounded-lg">
              <div className="flex items-center justify-between">
                <Select
                  value={solution.language}
                  onValueChange={(v) => {
                    const newSolutions = [...baseForm.solutions];
                    newSolutions[index] = { ...newSolutions[index], language: v };
                    setBaseForm({ ...baseForm, solutions: newSolutions });
                  }}
                >
                  <SelectTrigger className="w-[150px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {languageOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {baseForm.solutions.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="text-destructive"
                    onClick={() => {
                      setBaseForm({
                        ...baseForm,
                        solutions: baseForm.solutions.filter((_, i) => i !== index),
                      });
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
              <Textarea
                value={solution.code}
                onChange={(e) => {
                  const newSolutions = [...baseForm.solutions];
                  newSolutions[index] = { ...newSolutions[index], code: e.target.value };
                  setBaseForm({ ...baseForm, solutions: newSolutions });
                }}
                placeholder="솔루션 코드"
                rows={10}
                className="font-mono text-sm"
              />
            </div>
          ))}
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setBaseForm({
                ...baseForm,
                solutions: [...baseForm.solutions, { language: 'python', code: '' }],
              });
            }}
          >
            <Plus className="h-4 w-4 mr-2" />
            솔루션 추가
          </Button>
        </div>

        {/* 시간/메모리 제한 */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">시간 제한</label>
            <Input
              value={baseForm.time_limit}
              onChange={(e) => setBaseForm({ ...baseForm, time_limit: e.target.value })}
              placeholder="예: 1초"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">메모리 제한</label>
            <Input
              value={baseForm.memory_limit}
              onChange={(e) => setBaseForm({ ...baseForm, memory_limit: e.target.value })}
              placeholder="예: 256MB"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderBlankForm = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">빈칸 채우기 문제 생성</h2>
        <p className="text-muted-foreground">
          코드 템플릿에서 빈칸으로 만들 부분을 정의하세요
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">
            코드 템플릿 (빈칸 위치에 [BLANK] 사용)
          </label>
          <Textarea
            value={blankForm.code_template}
            onChange={(e) =>
              setBlankForm({ ...blankForm, code_template: e.target.value })
            }
            placeholder="def example():\n    return [BLANK]"
            rows={10}
            className="font-mono text-sm"
          />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">빈칸 정답</label>
            <Button size="sm" variant="outline" onClick={addBlank}>
              <Plus className="h-4 w-4 mr-2" />
              빈칸 추가
            </Button>
          </div>

          <AnimatePresence>
            {blankForm.blanks.map((blank, index) => (
              <motion.div
                key={blank.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex gap-3 items-start p-3 border rounded-lg"
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-sm font-medium">
                  {index + 1}
                </div>
                <div className="flex-1 grid gap-3 md:grid-cols-2">
                  <Input
                    value={blank.answer}
                    onChange={(e) => updateBlank(blank.id, 'answer', e.target.value)}
                    placeholder="정답"
                  />
                  <Input
                    value={blank.hint || ''}
                    onChange={(e) => updateBlank(blank.id, 'hint', e.target.value)}
                    placeholder="힌트 (선택)"
                  />
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  className="text-destructive"
                  onClick={() => removeBlank(blank.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </motion.div>
            ))}
          </AnimatePresence>

          {blankForm.blanks.length === 0 && (
            <div className="text-center py-8 text-muted-foreground border rounded-lg border-dashed">
              빈칸을 추가하여 문제를 구성하세요
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderPuzzleForm = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">퍼즐 문제 생성</h2>
        <p className="text-muted-foreground">
          코드 블록을 정의하고 올바른 순서를 지정하세요
        </p>
      </div>

      <div className="space-y-4">
        {/* 언어 선택 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">언어</label>
          <Select
            value={puzzleForm.language}
            onValueChange={(v) => setPuzzleForm({ ...puzzleForm, language: v })}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {languageOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* 고정 시작 코드 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">고정 시작 코드 (선택)</label>
          <Textarea
            value={puzzleForm.fixed_start}
            onChange={(e) => setPuzzleForm({ ...puzzleForm, fixed_start: e.target.value })}
            placeholder="블록 이전에 항상 표시되는 코드"
            rows={3}
            className="font-mono text-sm"
          />
        </div>

        {/* 코드 블록 */}
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">코드 블록 (올바른 순서로 입력)</label>
          <Button size="sm" variant="outline" onClick={addPuzzleBlock}>
            <Plus className="h-4 w-4 mr-2" />
            블록 추가
          </Button>
        </div>

        <AnimatePresence>
          {puzzleForm.blocks.map((block, index) => (
            <motion.div
              key={block.id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="flex gap-3 items-start p-3 border rounded-lg"
            >
              <div className="flex items-center gap-2">
                <GripVertical className="h-4 w-4 text-muted-foreground" />
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-sm font-medium">
                  {index + 1}
                </div>
              </div>
              <div className="flex-1">
                <Input
                  value={block.code}
                  onChange={(e) => updatePuzzleBlock(block.id, 'code', e.target.value)}
                  placeholder="코드 블록 내용"
                  className="font-mono text-sm"
                />
              </div>
              <Button
                size="icon"
                variant="ghost"
                className="text-destructive"
                onClick={() => removePuzzleBlock(block.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </motion.div>
          ))}
        </AnimatePresence>

        {puzzleForm.blocks.length === 0 && (
          <div className="text-center py-8 text-muted-foreground border rounded-lg border-dashed">
            블록을 추가하여 문제를 구성하세요
          </div>
        )}

        {/* 고정 종료 코드 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">고정 종료 코드 (선택)</label>
          <Textarea
            value={puzzleForm.fixed_end}
            onChange={(e) => setPuzzleForm({ ...puzzleForm, fixed_end: e.target.value })}
            placeholder="블록 이후에 항상 표시되는 코드"
            rows={3}
            className="font-mono text-sm"
          />
        </div>
      </div>
    </div>
  );

  const renderGuidedForm = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">가이드 문제 생성</h2>
        <p className="text-muted-foreground">
          학습자를 위한 개념 설명과 접근법을 정의하세요
        </p>
      </div>

      <div className="space-y-4">
        {/* 언어 선택 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">언어</label>
          <Select
            value={guidedForm.language}
            onValueChange={(v) => setGuidedForm({ ...guidedForm, language: v })}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {languageOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* 개념 설명 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">개념 설명 *</label>
          <Textarea
            value={guidedForm.concept_explanation}
            onChange={(e) => setGuidedForm({ ...guidedForm, concept_explanation: e.target.value })}
            placeholder="이 문제에서 다루는 핵심 개념을 설명하세요"
            rows={4}
          />
        </div>

        {/* 변수 가이드 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">변수 가이드</label>
            <Button size="sm" variant="outline" onClick={addVariableGuide}>
              <Plus className="h-4 w-4 mr-2" />
              변수 추가
            </Button>
          </div>

          <AnimatePresence>
            {guidedForm.variables_guide.map((variable, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-4 border rounded-lg space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">변수 {index + 1}</span>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="text-destructive"
                    onClick={() => removeVariableGuide(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <Input
                    value={variable.name}
                    onChange={(e) => updateVariableGuide(index, 'name', e.target.value)}
                    placeholder="변수 이름 (예: result)"
                  />
                  <Input
                    value={variable.type}
                    onChange={(e) => updateVariableGuide(index, 'type', e.target.value)}
                    placeholder="타입 (예: list)"
                  />
                </div>
                <Input
                  value={variable.role}
                  onChange={(e) => updateVariableGuide(index, 'role', e.target.value)}
                  placeholder="역할 (예: 최종 결과를 저장하는 리스트)"
                />
                <Input
                  value={variable.initial || ''}
                  onChange={(e) => updateVariableGuide(index, 'initial', e.target.value)}
                  placeholder="초기값 (선택, 예: [])"
                />
              </motion.div>
            ))}
          </AnimatePresence>

          {guidedForm.variables_guide.length === 0 && (
            <div className="text-center py-4 text-muted-foreground text-sm border rounded-lg border-dashed">
              변수 가이드를 추가하면 학습자가 각 변수의 역할을 이해하는데 도움이 됩니다
            </div>
          )}
        </div>

        {/* 접근법 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">접근법 *</label>
          <Textarea
            value={guidedForm.approach_guide}
            onChange={(e) => setGuidedForm({ ...guidedForm, approach_guide: e.target.value })}
            placeholder="문제를 해결하는 방법을 단계별로 설명하세요"
            rows={6}
          />
        </div>

        {/* 시작 코드 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">시작 코드 *</label>
          <Textarea
            value={guidedForm.starter_code}
            onChange={(e) => setGuidedForm({ ...guidedForm, starter_code: e.target.value })}
            placeholder="학습자에게 제공할 초기 코드 템플릿"
            rows={8}
            className="font-mono text-sm"
          />
        </div>
      </div>
    </div>
  );

  const handleNext = () => {
    if (step === 1) {
      if (problemType === 'base') {
        setStep(2);
      } else if (originalIdParam) {
        setStep(2);
      }
    }
  };

  const handleSubmit = () => {
    switch (problemType) {
      case 'base':
        handleCreateBase();
        break;
      case 'blank':
        handleCreateBlank();
        break;
      case 'puzzle':
        handleCreatePuzzle();
        break;
      case 'guided':
        handleCreateGuided();
        break;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin/problems">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">새 문제 생성</h1>
          <p className="text-muted-foreground">
            {originalIdParam
              ? '기존 문제에 변형을 추가합니다'
              : '새로운 문제를 생성합니다'}
          </p>
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2">
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full ${
            step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted'
          }`}
        >
          {step > 1 ? <Check className="h-4 w-4" /> : '1'}
        </div>
        <div
          className={`flex-1 h-1 rounded ${step > 1 ? 'bg-primary' : 'bg-muted'}`}
        />
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full ${
            step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted'
          }`}
        >
          2
        </div>
      </div>

      {/* Content */}
      <Card>
        <CardContent className="pt-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              {step === 1 && renderTypeSelection()}
              {step === 2 && problemType === 'base' && renderBaseForm()}
              {step === 2 && problemType === 'blank' && renderBlankForm()}
              {step === 2 && problemType === 'puzzle' && renderPuzzleForm()}
              {step === 2 && problemType === 'guided' && renderGuidedForm()}
            </motion.div>
          </AnimatePresence>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setStep(1)}
          disabled={step === 1}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          이전
        </Button>

        {step === 1 ? (
          <Button
            onClick={handleNext}
            disabled={
              problemType !== 'base' && !originalIdParam
            }
          >
            다음
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? '생성 중...' : '문제 생성'}
            <Check className="h-4 w-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  );
}
