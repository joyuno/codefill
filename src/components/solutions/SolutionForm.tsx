'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { solutionsApi } from '@/lib/api';
import { Loader2 } from 'lucide-react';

interface SolutionFormProps {
  baseProblemId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

const languages = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
];

export function SolutionForm({ baseProblemId, onSuccess, onCancel }: SolutionFormProps) {
  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!code.trim()) {
      setError('코드를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await solutionsApi.createSolution({
        base_problem_id: baseProblemId,
        language,
        code: code.trim(),
        title: title.trim() || undefined,
        description: description.trim() || undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : '풀이 등록에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border border-border rounded-lg p-4 bg-card space-y-4">
      <h3 className="font-semibold">내 풀이 작성</h3>

      {error && (
        <div className="text-sm text-destructive bg-destructive/10 px-3 py-2 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="title">제목 (선택)</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="예: O(n) 풀이"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="language">언어</Label>
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {languages.map((lang) => (
                <SelectItem key={lang.value} value={lang.value}>
                  {lang.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="code">코드 *</Label>
        <Textarea
          id="code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="풀이 코드를 입력하세요..."
          className="font-mono min-h-[200px]"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">설명 (선택)</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="풀이에 대한 설명을 추가하세요..."
          className="min-h-[80px]"
        />
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          취소
        </Button>
        <Button type="submit" disabled={loading}>
          {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
          등록하기
        </Button>
      </div>
    </form>
  );
}
