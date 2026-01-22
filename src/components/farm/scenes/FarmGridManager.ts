/**
 * FarmGridManager - 그리드 기반 밭 시스템
 * farm_size에 따라 밭 그리드를 렌더링하고 작물을 관리
 *
 * 확장 단계: 1x1 -> 2x2 -> 3x3 -> 4x4 -> 5x5
 */

import * as Phaser from 'phaser';
import {
  TILE_SIZE,
  MAP_WIDTH,
  MAP_HEIGHT,
  FARM_TILESET,
  FARM_TILES,
  FARM_OFFSET_X,
  FARM_OFFSET_Y,
} from '../config/gameConfig';
import { DEPTH, getCropDepth } from '../config/depthConfig';
import { getCropConfig, getCropFrame, getCropSpriteKey, CROP_ASSET_PATH, CROPS } from '../config/cropConfig';

// 슬롯 데이터 타입 (백엔드와 동일)
export interface FarmSlot {
  slot: number;
  cropCode: string | null;
  plantedAt: string | null;
  growTimeSeconds: number | null;
  stage: number;
}

// 내부 슬롯 스프라이트 관리
interface SlotSprites {
  soil: Phaser.GameObjects.Sprite;
  crop: Phaser.GameObjects.Sprite | null;
  timerContainer: Phaser.GameObjects.Container | null;
  timerProgress: Phaser.GameObjects.Graphics | null;
}

export class FarmGridManager {
  private scene: Phaser.Scene;

  // 슬롯 스프라이트 저장
  private slotSprites: Map<number, SlotSprites> = new Map();

  // 테두리 스프라이트
  private borderSprites: Phaser.GameObjects.Sprite[] = [];

  // 현재 farm_size
  private currentFarmSize: number = 0;

  // 타이머 업데이트 간격
  private lastTimerUpdate: number = 0;
  private readonly TIMER_UPDATE_INTERVAL = 1000;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드 (지연 로딩 적용)
   * @param farmSlots 현재 심어진 작물 슬롯
   * @param inventory 보유한 씨앗 목록
   */
  preload(farmSlots?: FarmSlot[], inventory?: { itemCode: string; quantity: number }[]): void {
    // 밭 타일셋
    if (!this.scene.textures.exists(FARM_TILESET.key)) {
      this.scene.load.spritesheet(FARM_TILESET.key, FARM_TILESET.path, {
        frameWidth: FARM_TILESET.frameWidth,
        frameHeight: FARM_TILESET.frameHeight,
      });
    }

    // 필요한 작물만 추출 (심어진 작물 + 보유 씨앗)
    const neededCrops = new Set<string>();

    // 1. 심어진 작물
    if (farmSlots) {
      farmSlots.forEach(slot => {
        if (slot.cropCode) {
          neededCrops.add(slot.cropCode);
        }
      });
    }

    // 2. 보유한 씨앗 (seed_tomato -> tomato)
    if (inventory) {
      inventory.forEach(item => {
        if (item.itemCode.startsWith('seed_') && item.quantity > 0) {
          const cropCode = item.itemCode.replace('seed_', '');
          neededCrops.add(cropCode);
        }
      });
    }

    // 필요한 작물만 로드 (없으면 기본 3종만)
    const cropsToLoad = neededCrops.size > 0
      ? Array.from(neededCrops)
      : ['carrot', 'tomato', 'radish']; // 기본 작물

    cropsToLoad.forEach(cropCode => {
      const crop = CROPS[cropCode];
      if (!crop) return;

      const key = getCropSpriteKey(crop.code);
      if (!this.scene.textures.exists(key)) {
        const spritePath = crop.spritesheet.startsWith('/')
          ? crop.spritesheet
          : CROP_ASSET_PATH + crop.spritesheet;
        this.scene.load.spritesheet(key, spritePath, {
          frameWidth: crop.frameWidth,
          frameHeight: crop.frameHeight,
        });
      }
    });
  }

  /**
   * 런타임 중 추가 작물 로드 (새 씨앗 획득 시)
   */
  loadCropAsset(cropCode: string): Promise<void> {
    return new Promise((resolve) => {
      const crop = CROPS[cropCode];
      if (!crop) {
        resolve();
        return;
      }

      const key = getCropSpriteKey(crop.code);
      if (this.scene.textures.exists(key)) {
        resolve();
        return;
      }

      const spritePath = crop.spritesheet.startsWith('/')
        ? crop.spritesheet
        : CROP_ASSET_PATH + crop.spritesheet;

      this.scene.load.spritesheet(key, spritePath, {
        frameWidth: crop.frameWidth,
        frameHeight: crop.frameHeight,
      });

      this.scene.load.once('complete', () => {
        resolve();
      });

      this.scene.load.start();
    });
  }

  /**
   * 밭 그리드 렌더링
   */
  renderGrid(farmSize: number, farmSlots: FarmSlot[]): void {
    // 기존 스프라이트 정리
    this.clearGrid();

    this.currentFarmSize = farmSize;
    const gridWidth = Math.sqrt(farmSize);

    // 각 슬롯 렌더링
    for (let i = 0; i < farmSize; i++) {
      const col = i % gridWidth;
      const row = Math.floor(i / gridWidth);
      const tileX = FARM_OFFSET_X + col;
      const tileY = FARM_OFFSET_Y + row;

      // 밭 타일 스프라이트
      const worldX = tileX * TILE_SIZE + TILE_SIZE / 2;
      const worldY = tileY * TILE_SIZE + TILE_SIZE / 2;

      const soilSprite = this.scene.add.sprite(
        worldX,
        worldY,
        FARM_TILESET.key,
        FARM_TILES.CENTER
      );
      soilSprite.setDepth(DEPTH.SOIL_TILES);

      // 슬롯 데이터 확인
      const slotData = farmSlots.find(s => s.slot === i);
      let cropSprite: Phaser.GameObjects.Sprite | null = null;
      let timerContainer: Phaser.GameObjects.Container | null = null;
      let timerProgress: Phaser.GameObjects.Graphics | null = null;

      if (slotData?.cropCode) {
        // 작물 스프라이트
        const cropConfig = getCropConfig(slotData.cropCode);
        if (cropConfig) {
          // stage 그대로 사용 (0 = 씨앗)
          const stage = slotData.stage;
          const frame = getCropFrame(slotData.cropCode, stage);
          cropSprite = this.scene.add.sprite(
            worldX,
            worldY + cropConfig.offsetY,
            getCropSpriteKey(slotData.cropCode),
            frame
          );
          cropSprite.setDepth(getCropDepth(worldY, MAP_HEIGHT));

          // 성장 중인 경우 타이머 표시 (보정된 stage 사용)
          if (stage < 6 && slotData.plantedAt && slotData.growTimeSeconds) {
            const timerResult = this.createTimerIndicator(worldX, worldY, slotData);
            timerContainer = timerResult.container;
            timerProgress = timerResult.progress;
          }
        }
      }

      this.slotSprites.set(i, {
        soil: soilSprite,
        crop: cropSprite,
        timerContainer,
        timerProgress,
      });
    }

    // 테두리 렌더링
    this.renderBorder(farmSize);
  }

  /**
   * 테두리 렌더링 (9-patch)
   */
  private renderBorder(farmSize: number): void {
    const gridWidth = Math.sqrt(farmSize);

    // 4모서리
    this.addBorderTile(FARM_OFFSET_X - 1, FARM_OFFSET_Y - 1, FARM_TILES.TOP_LEFT);
    this.addBorderTile(FARM_OFFSET_X + gridWidth, FARM_OFFSET_Y - 1, FARM_TILES.TOP_RIGHT);
    this.addBorderTile(FARM_OFFSET_X - 1, FARM_OFFSET_Y + gridWidth, FARM_TILES.BOTTOM_LEFT);
    this.addBorderTile(FARM_OFFSET_X + gridWidth, FARM_OFFSET_Y + gridWidth, FARM_TILES.BOTTOM_RIGHT);

    // 상단/하단 가장자리
    for (let i = 0; i < gridWidth; i++) {
      this.addBorderTile(FARM_OFFSET_X + i, FARM_OFFSET_Y - 1, FARM_TILES.TOP);
      this.addBorderTile(FARM_OFFSET_X + i, FARM_OFFSET_Y + gridWidth, FARM_TILES.BOTTOM);
    }

    // 좌측/우측 가장자리
    for (let i = 0; i < gridWidth; i++) {
      this.addBorderTile(FARM_OFFSET_X - 1, FARM_OFFSET_Y + i, FARM_TILES.LEFT);
      this.addBorderTile(FARM_OFFSET_X + gridWidth, FARM_OFFSET_Y + i, FARM_TILES.RIGHT);
    }
  }

  /**
   * 테두리 타일 추가
   */
  private addBorderTile(tileX: number, tileY: number, frame: number): void {
    const worldX = tileX * TILE_SIZE + TILE_SIZE / 2;
    const worldY = tileY * TILE_SIZE + TILE_SIZE / 2;

    const sprite = this.scene.add.sprite(worldX, worldY, FARM_TILESET.key, frame);
    sprite.setDepth(DEPTH.SOIL_TILES - 1);
    this.borderSprites.push(sprite);
  }

  /**
   * 타이머 인디케이터 생성 (시계 아이콘 + 원형 프로그레스)
   */
  private createTimerIndicator(
    worldX: number,
    worldY: number,
    slotData: FarmSlot
  ): { container: Phaser.GameObjects.Container; progress: Phaser.GameObjects.Graphics } {
    const radius = 8;
    const posX = worldX;
    const posY = worldY - TILE_SIZE / 2 - radius - 2;

    // 컨테이너 생성
    const container = this.scene.add.container(posX, posY);
    container.setDepth(DEPTH.INDICATOR);

    // 배경 원 (어두운 배경)
    const bgCircle = this.scene.add.graphics();
    bgCircle.fillStyle(0x000000, 0.6);
    bgCircle.fillCircle(0, 0, radius);
    container.add(bgCircle);

    // 프로그레스 링
    const progress = this.scene.add.graphics();
    container.add(progress);

    // 시계 아이콘 (중앙에 작은 원 + 시계 바늘)
    const clockIcon = this.scene.add.graphics();
    clockIcon.lineStyle(1.5, 0xffffff, 1);
    clockIcon.strokeCircle(0, 0, 4);
    // 시계 바늘
    clockIcon.lineStyle(1, 0xffffff, 1);
    clockIcon.lineBetween(0, 0, 0, -2.5); // 분침
    clockIcon.lineBetween(0, 0, 2, 0); // 시침
    container.add(clockIcon);

    // 초기 프로그레스 그리기
    this.drawProgress(progress, slotData, radius);

    return { container, progress };
  }

  /**
   * 원형 프로그레스 그리기
   */
  private drawProgress(graphics: Phaser.GameObjects.Graphics, slotData: FarmSlot, radius: number): void {
    graphics.clear();

    if (!slotData.plantedAt || !slotData.growTimeSeconds) return;

    const plantedAt = new Date(slotData.plantedAt).getTime();
    const growTimeMs = slotData.growTimeSeconds * 1000;
    const elapsed = Date.now() - plantedAt;
    const progressPercent = Math.min(1, elapsed / growTimeMs);

    // 프로그레스 색상 (진행률에 따라 변화)
    let color = 0xfbbf24; // 노란색 (기본)
    if (progressPercent >= 0.75) {
      color = 0x22c55e; // 녹색 (거의 완료)
    } else if (progressPercent >= 0.5) {
      color = 0x84cc16; // 연두색
    }

    // 원형 프로그레스 (시계 방향, 12시부터 시작)
    graphics.lineStyle(2, color, 1);
    const startAngle = -Math.PI / 2; // 12시 방향
    const endAngle = startAngle + (progressPercent * Math.PI * 2);
    graphics.beginPath();
    graphics.arc(0, 0, radius - 1, startAngle, endAngle, false);
    graphics.strokePath();
  }

  /**
   * 남은 시간 계산 (밀리초)
   */
  private calculateRemainingTime(slotData: FarmSlot): number {
    if (!slotData.plantedAt || !slotData.growTimeSeconds) return 0;

    const plantedAt = new Date(slotData.plantedAt).getTime();
    const growTimeMs = slotData.growTimeSeconds * 1000;
    const elapsed = Date.now() - plantedAt;
    return Math.max(0, growTimeMs - elapsed);
  }

  /**
   * 특정 슬롯 업데이트
   */
  updateSlot(slot: number, slotData: FarmSlot): void {
    const sprites = this.slotSprites.get(slot);
    if (!sprites) {
      return;
    }

    const gridWidth = Math.sqrt(this.currentFarmSize);
    const col = slot % gridWidth;
    const row = Math.floor(slot / gridWidth);
    const tileX = FARM_OFFSET_X + col;
    const tileY = FARM_OFFSET_Y + row;
    const worldX = tileX * TILE_SIZE + TILE_SIZE / 2;
    const worldY = tileY * TILE_SIZE + TILE_SIZE / 2;

    // 기존 작물/타이머 제거
    if (sprites.crop) {
      sprites.crop.destroy();
      sprites.crop = null;
    }
    if (sprites.timerContainer) {
      sprites.timerContainer.destroy();
      sprites.timerContainer = null;
      sprites.timerProgress = null;
    }

    // 새 작물 스프라이트
    if (slotData.cropCode) {
      const cropConfig = getCropConfig(slotData.cropCode);

      if (cropConfig) {
        const spriteKey = getCropSpriteKey(slotData.cropCode);
        const textureExists = this.scene.textures.exists(spriteKey);

        if (!textureExists) {
          return;
        }

        // stage 그대로 사용 (0 = 씨앗)
        const stage = slotData.stage;
        const frame = getCropFrame(slotData.cropCode, stage);

        sprites.crop = this.scene.add.sprite(
          worldX,
          worldY + cropConfig.offsetY,
          spriteKey,
          frame
        );
        const depth = getCropDepth(worldY, MAP_HEIGHT);
        sprites.crop.setDepth(depth);

        // 성장 중인 경우 타이머 표시
        if (stage < 6 && slotData.plantedAt && slotData.growTimeSeconds) {
          const timerResult = this.createTimerIndicator(worldX, worldY, slotData);
          sprites.timerContainer = timerResult.container;
          sprites.timerProgress = timerResult.progress;
        }
      }
    }
  }

  /**
   * 월드 좌표에서 슬롯 인덱스 반환
   */
  getSlotAt(worldX: number, worldY: number): number | null {
    const tileX = Math.floor(worldX / TILE_SIZE);
    const tileY = Math.floor(worldY / TILE_SIZE);

    const col = tileX - FARM_OFFSET_X;
    const row = tileY - FARM_OFFSET_Y;

    const gridWidth = Math.sqrt(this.currentFarmSize);

    if (col < 0 || row < 0 || col >= gridWidth || row >= gridWidth) {
      return null;
    }

    return row * gridWidth + col;
  }

  /**
   * 슬롯 중심 좌표 반환
   */
  getSlotCenter(slot: number): { x: number; y: number } | null {
    if (slot < 0 || slot >= this.currentFarmSize) return null;

    const gridWidth = Math.sqrt(this.currentFarmSize);
    const col = slot % gridWidth;
    const row = Math.floor(slot / gridWidth);
    const tileX = FARM_OFFSET_X + col;
    const tileY = FARM_OFFSET_Y + row;

    return {
      x: tileX * TILE_SIZE + TILE_SIZE / 2,
      y: tileY * TILE_SIZE + TILE_SIZE / 2,
    };
  }

  /**
   * 타이머 업데이트 (매 프레임 호출)
   */
  updateTimers(farmSlots: FarmSlot[]): void {
    const now = Date.now();
    if (now - this.lastTimerUpdate < this.TIMER_UPDATE_INTERVAL) return;
    this.lastTimerUpdate = now;

    for (const slotData of farmSlots) {
      const sprites = this.slotSprites.get(slotData.slot);
      if (!sprites) continue;

      // 성장 완료 체크
      if (slotData.stage < 6 && slotData.plantedAt && slotData.growTimeSeconds) {
        const remaining = this.calculateRemainingTime(slotData);

        // 성장 완료시 stage 업데이트 (프론트에서 계산)
        const plantedAt = new Date(slotData.plantedAt).getTime();
        const growTimeMs = slotData.growTimeSeconds * 1000;
        const elapsed = now - plantedAt;
        const progress = elapsed / growTimeMs;

        // 7단계 성장 (0~6)
        let newStage = 0;
        if (progress >= 1.0) newStage = 6;
        else if (progress >= 0.833) newStage = 5;
        else if (progress >= 0.667) newStage = 4;
        else if (progress >= 0.5) newStage = 3;
        else if (progress >= 0.333) newStage = 2;
        else if (progress >= 0.167) newStage = 1;
        else newStage = 0;

        // 스테이지 변경 시 작물 프레임 업데이트
        if (sprites.crop && slotData.cropCode && newStage !== slotData.stage) {
          const frame = getCropFrame(slotData.cropCode, newStage);
          sprites.crop.setFrame(frame);
          slotData.stage = newStage; // 로컬 업데이트
        }

        // 타이머 프로그레스 업데이트
        if (sprites.timerContainer && sprites.timerProgress) {
          if (remaining <= 0 || newStage >= 6) {
            sprites.timerContainer.destroy();
            sprites.timerContainer = null;
            sprites.timerProgress = null;
          } else {
            this.drawProgress(sprites.timerProgress, slotData, 8);
          }
        }
      }
    }
  }

  /**
   * 현재 farm size 반환
   */
  getFarmSize(): number {
    return this.currentFarmSize;
  }

  /**
   * 그리드 정리
   */
  clearGrid(): void {
    // 슬롯 스프라이트 제거
    this.slotSprites.forEach(sprites => {
      sprites.soil.destroy();
      if (sprites.crop) sprites.crop.destroy();
      if (sprites.timerContainer) sprites.timerContainer.destroy();
    });
    this.slotSprites.clear();

    // 테두리 스프라이트 제거
    this.borderSprites.forEach(sprite => sprite.destroy());
    this.borderSprites = [];
  }

  /**
   * 리소스 정리
   */
  destroy(): void {
    this.clearGrid();
  }
}
