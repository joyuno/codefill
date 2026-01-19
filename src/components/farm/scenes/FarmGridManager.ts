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
  timer: Phaser.GameObjects.Text | null;
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
   * 에셋 프리로드
   */
  preload(): void {
    // 밭 타일셋
    if (!this.scene.textures.exists(FARM_TILESET.key)) {
      this.scene.load.spritesheet(FARM_TILESET.key, FARM_TILESET.path, {
        frameWidth: FARM_TILESET.frameWidth,
        frameHeight: FARM_TILESET.frameHeight,
      });
    }

    // 작물 스프라이트시트
    Object.values(CROPS).forEach(crop => {
      const key = getCropSpriteKey(crop.code);
      if (!this.scene.textures.exists(key)) {
        // spritesheet 경로가 절대 경로이면 그대로 사용, 아니면 CROP_ASSET_PATH 추가
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
      let timerText: Phaser.GameObjects.Text | null = null;

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
            timerText = this.createTimerText(worldX, worldY, slotData);
          }
        }
      }

      this.slotSprites.set(i, {
        soil: soilSprite,
        crop: cropSprite,
        timer: timerText,
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
   * 타이머 텍스트 생성
   */
  private createTimerText(worldX: number, worldY: number, slotData: FarmSlot): Phaser.GameObjects.Text {
    const remaining = this.calculateRemainingTime(slotData);
    const text = this.formatTime(remaining);

    const timerText = this.scene.add.text(worldX, worldY - TILE_SIZE / 2 - 5, text, {
      fontSize: '10px',
      fontFamily: 'Arial',
      color: '#ffffff',
      backgroundColor: '#000000aa',
      padding: { x: 3, y: 2 },
    });
    timerText.setOrigin(0.5, 1);
    timerText.setDepth(DEPTH.INDICATOR);

    return timerText;
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
   * 시간 포맷팅 (mm:ss)
   */
  private formatTime(ms: number): string {
    const seconds = Math.ceil(ms / 1000);
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  }

  /**
   * 특정 슬롯 업데이트
   */
  updateSlot(slot: number, slotData: FarmSlot): void {
    console.log('[FarmGridManager] updateSlot:', { slot, slotData });

    const sprites = this.slotSprites.get(slot);
    if (!sprites) {
      console.warn('[FarmGridManager] No sprites found for slot:', slot);
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
    if (sprites.timer) {
      sprites.timer.destroy();
      sprites.timer = null;
    }

    // 새 작물 스프라이트
    if (slotData.cropCode) {
      const cropConfig = getCropConfig(slotData.cropCode);
      console.log('[FarmGridManager] cropConfig:', cropConfig);

      if (cropConfig) {
        const spriteKey = getCropSpriteKey(slotData.cropCode);
        const textureExists = this.scene.textures.exists(spriteKey);
        console.log('[FarmGridManager] texture check:', { spriteKey, textureExists });

        if (!textureExists) {
          console.error('[FarmGridManager] Texture not found:', spriteKey);
          return;
        }

        // stage가 0이면 1로 보정 (새로 심은 작물)
        const stage = slotData.stage === 0 ? 1 : slotData.stage;
        const frame = getCropFrame(slotData.cropCode, stage);
        console.log('[FarmGridManager] Creating crop sprite:', { worldX, worldY, spriteKey, frame, stage });

        sprites.crop = this.scene.add.sprite(
          worldX,
          worldY + cropConfig.offsetY,
          spriteKey,
          frame
        );
        const depth = getCropDepth(worldY, MAP_HEIGHT);
        sprites.crop.setDepth(depth);
        console.log('[FarmGridManager] Crop sprite created with depth:', depth);

        // 성장 중인 경우 타이머 표시
        if (stage < 6 && slotData.plantedAt && slotData.growTimeSeconds) {
          sprites.timer = this.createTimerText(worldX, worldY, slotData);
          console.log('[FarmGridManager] Timer created');
        }
      } else {
        console.error('[FarmGridManager] No crop config for:', slotData.cropCode);
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

        // 타이머 텍스트 업데이트
        if (sprites.timer) {
          if (remaining <= 0 || newStage >= 6) {
            sprites.timer.destroy();
            sprites.timer = null;
          } else {
            sprites.timer.setText(this.formatTime(remaining));
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
      if (sprites.timer) sprites.timer.destroy();
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
