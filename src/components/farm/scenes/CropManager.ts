/**
 * CropManager - 농장 밭과 작물 관리
 * 밭 렌더링, 작물 스프라이트, 성장 단계 표시
 */

import Phaser from 'phaser';
import {
  TILE_SIZE,
  MAP_WIDTH,
  MAP_HEIGHT,
  MAP_COLS,
  MAP_ROWS,
  TILESET,
  FARM_TILES,
} from '../config/gameConfig';
import { DEPTH, getCropDepth } from '../config/depthConfig';
import {
  CROPS,
  CROP_ASSET_PATH,
  getCropConfig,
  getCropFrame,
  getCropSpriteKey,
} from '../config/cropConfig';

// 밭 슬롯 데이터 (백엔드와 동일한 구조)
export interface FarmSlotData {
  slot: number;
  cropCode: string | null;
  plantedAt: string | null;
  stage: number;
  growTimeSeconds?: number;  // 작물별 성장 시간
}

export class CropManager {
  private scene: Phaser.Scene;
  private farmTiles: Phaser.GameObjects.Sprite[] = [];  // 9-patch 타일들
  private cropSprites: Map<number, Phaser.GameObjects.Sprite> = new Map();
  private timerTexts: Map<number, Phaser.GameObjects.Text> = new Map();  // 타이머 텍스트

  private currentFarmSize: number = 3;  // 심을 수 있는 칸 (N×N)
  private farmSlots: FarmSlotData[] = [];
  private lastTimerUpdate: number = 0;  // 마지막 타이머 업데이트 시간

  // 농장 시작 위치 (타일 좌표) - 동적 계산
  private farmStartCol: number = 0;
  private farmStartRow: number = 0;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    // 작물 스프라이트시트 로드
    Object.values(CROPS).forEach(crop => {
      this.scene.load.spritesheet(
        getCropSpriteKey(crop.code),
        CROP_ASSET_PATH + crop.spritesheet,
        {
          frameWidth: crop.frameWidth,
          frameHeight: crop.frameHeight,
        }
      );
    });
  }

  /**
   * 농장 생성
   * @param farmSize 심을 수 있는 칸 (1~5)
   */
  create(farmSize: number = 3): void {
    this.currentFarmSize = Math.min(Math.max(farmSize, 1), 5);  // 1x1 ~ 5x5
    this.createFarmField();
  }

  /**
   * 농장 밭 생성 (9-patch 방식)
   * N×N 밭 = (N+2)×(N+2) 타일 렌더링
   */
  private createFarmField(): void {
    // 기존 타일 정리
    this.farmTiles.forEach(sprite => sprite.destroy());
    this.farmTiles = [];

    const N = this.currentFarmSize;  // 심을 수 있는 칸
    const renderSize = N + 2;        // 실제 렌더링 크기 (테두리 포함)

    // 맵 중앙에 배치
    this.farmStartCol = Math.floor((MAP_COLS - renderSize) / 2);
    this.farmStartRow = Math.floor((MAP_ROWS - renderSize) / 2);

    // 9-patch 타일 배치
    for (let row = 0; row < renderSize; row++) {
      for (let col = 0; col < renderSize; col++) {
        const worldX = (this.farmStartCol + col) * TILE_SIZE + TILE_SIZE / 2;
        const worldY = (this.farmStartRow + row) * TILE_SIZE + TILE_SIZE / 2;

        const tileIndex = this.get9PatchTileIndex(col, row, renderSize);
        const tile = this.scene.add.sprite(worldX, worldY, TILESET.key, tileIndex);
        tile.setDepth(DEPTH.SOIL_TILES);
        this.farmTiles.push(tile);
      }
    }
  }

  /**
   * 9-patch 타일 인덱스 결정
   * renderSize = N + 2 (테두리 포함 크기)
   */
  private get9PatchTileIndex(col: number, row: number, renderSize: number): number {
    const isTop = row === 0;
    const isBottom = row === renderSize - 1;
    const isLeft = col === 0;
    const isRight = col === renderSize - 1;

    // 4 모서리
    if (isTop && isLeft) return FARM_TILES.TOP_LEFT;
    if (isTop && isRight) return FARM_TILES.TOP_RIGHT;
    if (isBottom && isLeft) return FARM_TILES.BOTTOM_LEFT;
    if (isBottom && isRight) return FARM_TILES.BOTTOM_RIGHT;

    // 4 테두리
    if (isTop) return FARM_TILES.TOP;
    if (isBottom) return FARM_TILES.BOTTOM;
    if (isLeft) return FARM_TILES.LEFT;
    if (isRight) return FARM_TILES.RIGHT;

    // 중앙 (심을 수 있는 칸)
    return FARM_TILES.CENTER;
  }

  /**
   * 슬롯 인덱스로 월드 좌표 계산
   * 심을 수 있는 칸은 테두리 안쪽 (farmStartCol + 1, farmStartRow + 1)
   */
  getSlotPosition(slotIndex: number): { x: number; y: number } {
    const col = slotIndex % this.currentFarmSize;
    const row = Math.floor(slotIndex / this.currentFarmSize);
    // 테두리 +1 오프셋
    const plantableStartCol = this.farmStartCol + 1;
    const plantableStartRow = this.farmStartRow + 1;
    return {
      x: (plantableStartCol + col) * TILE_SIZE + TILE_SIZE / 2,
      y: (plantableStartRow + row) * TILE_SIZE + TILE_SIZE / 2,
    };
  }

  /**
   * 월드 좌표로 슬롯 인덱스 찾기
   * @returns 슬롯 인덱스, 심을 수 있는 영역 밖이면 -1
   */
  getSlotAtPosition(worldX: number, worldY: number): number {
    // 심을 수 있는 칸의 시작 위치 (테두리 안쪽)
    const plantableStartCol = this.farmStartCol + 1;
    const plantableStartRow = this.farmStartRow + 1;

    const col = Math.floor(worldX / TILE_SIZE) - plantableStartCol;
    const row = Math.floor(worldY / TILE_SIZE) - plantableStartRow;

    if (col < 0 || col >= this.currentFarmSize || row < 0 || row >= this.currentFarmSize) {
      return -1;
    }

    return row * this.currentFarmSize + col;
  }

  /**
   * 농장 데이터 업데이트 (백엔드에서 받은 데이터)
   */
  updateFarmData(slots: FarmSlotData[]): void {
    this.farmSlots = slots;

    // 기존 작물 스프라이트 정리
    this.cropSprites.forEach(sprite => sprite.destroy());
    this.cropSprites.clear();

    // 기존 타이머 텍스트 정리
    this.timerTexts.forEach(text => text.destroy());
    this.timerTexts.clear();

    // 새 작물 스프라이트 생성
    slots.forEach(slot => {
      if (slot.cropCode && slot.stage >= 0) {
        this.createCropSprite(slot);
      }
    });
  }

  /**
   * 작물 스프라이트 생성
   */
  private createCropSprite(slot: FarmSlotData): void {
    const cropConfig = getCropConfig(slot.cropCode!);
    if (!cropConfig) return;

    const pos = this.getSlotPosition(slot.slot);
    const frame = getCropFrame(slot.cropCode!, slot.stage);

    const sprite = this.scene.add.sprite(
      pos.x,
      pos.y + cropConfig.offsetY,
      getCropSpriteKey(slot.cropCode!),
      frame
    );

    // Y좌표 기반 깊이 설정
    const depth = getCropDepth(pos.y, MAP_HEIGHT);
    sprite.setDepth(depth);

    this.cropSprites.set(slot.slot, sprite);

    // 타이머 텍스트 생성 (성장 중인 작물만)
    if (slot.stage < 4 && slot.plantedAt && slot.growTimeSeconds) {
      this.createTimerText(slot);
    }
  }

  /**
   * 타이머 텍스트 생성
   */
  private createTimerText(slot: FarmSlotData): void {
    const pos = this.getSlotPosition(slot.slot);

    // 기존 타이머 제거
    const existingTimer = this.timerTexts.get(slot.slot);
    if (existingTimer) {
      existingTimer.destroy();
    }

    const timerText = this.scene.add.text(
      pos.x,
      pos.y - TILE_SIZE / 2 - 8,
      '',
      {
        fontSize: '10px',
        fontFamily: 'monospace',
        color: '#FBBF24',
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        padding: { x: 3, y: 1 },
      }
    );
    timerText.setOrigin(0.5, 1);
    timerText.setDepth(DEPTH.HIGHLIGHT);

    this.timerTexts.set(slot.slot, timerText);
  }

  /**
   * 남은 시간 계산
   */
  private getRemainingTime(plantedAt: string, growTimeSeconds: number): number {
    const planted = new Date(plantedAt).getTime();
    const now = Date.now();
    const elapsed = (now - planted) / 1000;
    return Math.max(0, Math.ceil(growTimeSeconds - elapsed));
  }

  /**
   * 시간 포맷 (MM:SS)
   */
  private formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  /**
   * 매 프레임 타이머 업데이트
   */
  update(): void {
    const now = Date.now();
    // 1초에 한 번만 업데이트
    if (now - this.lastTimerUpdate < 1000) return;
    this.lastTimerUpdate = now;

    this.farmSlots.forEach(slot => {
      if (slot.cropCode && slot.plantedAt && slot.growTimeSeconds && slot.stage < 4) {
        const remaining = this.getRemainingTime(slot.plantedAt, slot.growTimeSeconds);
        const timerText = this.timerTexts.get(slot.slot);

        if (remaining > 0) {
          if (timerText) {
            timerText.setText(this.formatTime(remaining));
            timerText.setVisible(true);
          } else {
            // 타이머 텍스트가 없으면 생성
            this.createTimerText(slot);
          }
        } else {
          // 성장 완료 - 타이머 숨기기
          if (timerText) {
            timerText.setVisible(false);
          }
        }
      }
    });
  }

  /**
   * 특정 슬롯 작물 업데이트
   */
  updateSlot(slotIndex: number, cropCode: string | null, stage: number): void {
    // 기존 스프라이트 제거
    const existingSprite = this.cropSprites.get(slotIndex);
    if (existingSprite) {
      existingSprite.destroy();
      this.cropSprites.delete(slotIndex);
    }

    // 기존 타이머 제거
    const existingTimer = this.timerTexts.get(slotIndex);
    if (existingTimer) {
      existingTimer.destroy();
      this.timerTexts.delete(slotIndex);
    }

    // 새 작물 생성
    if (cropCode) {
      this.createCropSprite({
        slot: slotIndex,
        cropCode,
        plantedAt: null,
        stage,
      });
    }

    // 내부 데이터 업데이트
    const slotData = this.farmSlots.find(s => s.slot === slotIndex);
    if (slotData) {
      slotData.cropCode = cropCode;
      slotData.stage = stage;
    }
  }

  /**
   * 수확 이펙트 (파티클)
   */
  playHarvestEffect(slotIndex: number): void {
    const pos = this.getSlotPosition(slotIndex);

    // 간단한 반짝임 이펙트
    const particles = [];
    for (let i = 0; i < 5; i++) {
      const particle = this.scene.add.circle(
        pos.x + (Math.random() - 0.5) * TILE_SIZE,
        pos.y + (Math.random() - 0.5) * TILE_SIZE,
        4,
        0xffff00,
        1
      );
      particle.setDepth(DEPTH.HIGHLIGHT);
      particles.push(particle);
    }

    // 페이드아웃 후 제거
    this.scene.tweens.add({
      targets: particles,
      alpha: 0,
      y: '-=20',
      duration: 500,
      onComplete: () => {
        particles.forEach(p => p.destroy());
      },
    });
  }

  /**
   * 특정 슬롯 데이터 가져오기
   */
  getSlotData(slotIndex: number): FarmSlotData | undefined {
    return this.farmSlots.find(s => s.slot === slotIndex);
  }

  /**
   * 현재 농장 크기
   */
  getFarmSize(): number {
    return this.currentFarmSize;
  }

  /**
   * 농장 크기 변경 (확장)
   */
  setFarmSize(size: number): void {
    if (size !== this.currentFarmSize) {
      this.currentFarmSize = Math.min(Math.max(size, 1), 5);  // 1x1 ~ 5x5
      this.createFarmField();

      // 기존 작물 다시 그리기
      const currentSlots = [...this.farmSlots];
      this.updateFarmData(currentSlots);
    }
  }

  /**
   * 정리
   */
  destroy(): void {
    this.cropSprites.forEach(sprite => sprite.destroy());
    this.cropSprites.clear();
    this.timerTexts.forEach(text => text.destroy());
    this.timerTexts.clear();
    this.farmTiles.forEach(tile => tile.destroy());
    this.farmTiles = [];
  }
}
