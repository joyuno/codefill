'use client';

import { useState, useCallback } from 'react';
import Cropper, { Area } from 'react-easy-crop';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Loader2, Upload, Trash2, ZoomIn, AlertTriangle } from 'lucide-react';

interface AvatarEditModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentAvatarUrl?: string;
  username: string;
  avatarColor: string;
  onSave: (file: File) => Promise<void>;
  onDelete?: () => Promise<void>;
}

// Canvas를 사용해 이미지 크롭
async function getCroppedImg(
  imageSrc: string,
  pixelCrop: Area
): Promise<Blob> {
  const image = await createImage(imageSrc);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error('Canvas context not available');
  }

  // 출력 크기 설정 (정사각형 아바타)
  const outputSize = 256;
  canvas.width = outputSize;
  canvas.height = outputSize;

  // 크롭된 영역을 캔버스에 그리기
  ctx.drawImage(
    image,
    pixelCrop.x,
    pixelCrop.y,
    pixelCrop.width,
    pixelCrop.height,
    0,
    0,
    outputSize,
    outputSize
  );

  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Canvas to Blob failed'));
        }
      },
      'image/jpeg',
      0.9
    );
  });
}

function createImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener('load', () => resolve(image));
    image.addEventListener('error', (error) => reject(error));
    image.src = url;
  });
}

export function AvatarEditModal({
  open,
  onOpenChange,
  currentAvatarUrl,
  username,
  avatarColor,
  onSave,
  onDelete,
}: AvatarEditModalProps) {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [error, setError] = useState('');

  const hasCustomAvatar = currentAvatarUrl?.startsWith('http');

  const onCropComplete = useCallback((_: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 파일 타입 검증
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('JPEG, PNG, GIF, WebP 형식만 지원합니다.');
      return;
    }

    // 파일 크기 검증 (10MB - 크롭 전이라 여유있게)
    if (file.size > 10 * 1024 * 1024) {
      setError('파일 크기는 10MB 이하여야 합니다.');
      return;
    }

    setError('');
    const reader = new FileReader();
    reader.addEventListener('load', () => {
      setImageSrc(reader.result as string);
      setZoom(1);
      setCrop({ x: 0, y: 0 });
    });
    reader.readAsDataURL(file);
  };

  const resetState = useCallback(() => {
    setImageSrc(null);
    setZoom(1);
    setCrop({ x: 0, y: 0 });
    setCroppedAreaPixels(null);
    setError('');
    setSaving(false);
    setDeleting(false);
    setConfirmDelete(false);
  }, []);

  const handleOpenChange = useCallback((isOpen: boolean) => {
    if (!isOpen) {
      resetState();
    }
    onOpenChange(isOpen);
  }, [onOpenChange, resetState]);

  const handleSave = async () => {
    if (!imageSrc || !croppedAreaPixels) return;

    setSaving(true);
    setError('');

    try {
      const croppedBlob = await getCroppedImg(imageSrc, croppedAreaPixels);
      const file = new File([croppedBlob], 'avatar.jpg', { type: 'image/jpeg' });
      await onSave(file);
      toast.success('프로필 사진이 변경되었습니다.');
      handleOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : '이미지 저장에 실패했습니다.');
      setSaving(false);
    }
  };

  const handleDeleteClick = () => {
    setConfirmDelete(true);
  };

  const handleDeleteConfirm = async () => {
    if (!onDelete) return;

    setDeleting(true);
    setError('');

    try {
      await onDelete();
      toast.success('프로필 사진이 삭제되었습니다.');
      handleOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : '이미지 삭제에 실패했습니다.');
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setConfirmDelete(false);
  };

  const handleCancel = () => {
    if (imageSrc) {
      // 이미지 선택 상태에서 취소하면 선택 해제
      setImageSrc(null);
      setZoom(1);
      setCrop({ x: 0, y: 0 });
      setError('');
    } else {
      // 초기 상태에서 취소하면 모달 닫기
      handleOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        {confirmDelete ? (
          // 삭제 확인 화면
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                프로필 사진 삭제
              </DialogTitle>
              <DialogDescription>
                프로필 사진을 삭제하시겠습니까? 기본 아바타로 변경됩니다.
              </DialogDescription>
            </DialogHeader>

            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleDeleteCancel}
                disabled={deleting}
              >
                취소
              </Button>
              <Button
                type="button"
                variant="destructive"
                onClick={handleDeleteConfirm}
                disabled={deleting}
              >
                {deleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                삭제
              </Button>
            </div>
          </>
        ) : (
          // 기본 편집 화면
          <>
            <DialogHeader>
              <DialogTitle>프로필 사진 변경</DialogTitle>
              <DialogDescription>
                새로운 프로필 사진을 선택하고 원하는 영역을 조정하세요.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {imageSrc ? (
                // 크롭 인터페이스
                <>
                  <div className="relative h-64 w-full overflow-hidden rounded-lg bg-muted">
                    <Cropper
                      image={imageSrc}
                      crop={crop}
                      zoom={zoom}
                      aspect={1}
                      cropShape="round"
                      showGrid={false}
                      onCropChange={setCrop}
                      onCropComplete={onCropComplete}
                      onZoomChange={setZoom}
                    />
                  </div>

                  {/* 줌 슬라이더 */}
                  <div className="flex items-center gap-3">
                    <ZoomIn className="h-4 w-4 text-muted-foreground" />
                    <Slider
                      value={[zoom]}
                      min={1}
                      max={3}
                      step={0.1}
                      onValueChange={(value) => setZoom(value[0])}
                      className="flex-1"
                    />
                    <span className="w-12 text-right text-sm text-muted-foreground">
                      {Math.round(zoom * 100)}%
                    </span>
                  </div>
                </>
              ) : (
                // 현재 아바타 표시 & 업로드 버튼
                <div className="flex flex-col items-center gap-4 py-4">
                  <Avatar className="h-32 w-32">
                    <AvatarImage src={currentAvatarUrl} alt={username} />
                    <AvatarFallback
                      className="text-4xl font-bold text-primary-foreground"
                      style={{
                        backgroundColor: avatarColor.startsWith('hsl')
                          ? avatarColor
                          : 'hsl(142, 71%, 45%)',
                      }}
                    >
                      {username.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>

                  <label className="cursor-pointer">
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/gif,image/webp"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <Button type="button" variant="outline" className="gap-2" asChild>
                      <span>
                        <Upload className="h-4 w-4" />
                        이미지 선택
                      </span>
                    </Button>
                  </label>
                </div>
              )}

              {error && (
                <p className="text-center text-sm text-destructive">{error}</p>
              )}

              {/* 버튼 영역 */}
              <div className="flex justify-between">
                {/* 삭제 버튼 (커스텀 아바타가 있을 때만) */}
                <div>
                  {hasCustomAvatar && onDelete && !imageSrc && (
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      onClick={handleDeleteClick}
                      className="gap-1"
                    >
                      <Trash2 className="h-4 w-4" />
                      삭제
                    </Button>
                  )}
                </div>

                {/* 취소/저장 버튼 */}
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    {imageSrc ? '다시 선택' : '취소'}
                  </Button>
                  {imageSrc && (
                    <Button
                      type="button"
                      onClick={handleSave}
                      disabled={saving || !croppedAreaPixels}
                    >
                      {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      저장
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
