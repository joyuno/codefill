/**
 * UnifiedPlacementManager - 통합 배치 시스템
 * 건물, 나무, 장식, 울타리, 밭 등 모든 배치 가능 아이템 관리
 *
 * 기존 BuildingManager + PlacementSystem + CropManager 밭 기능 통합
 */

import Phaser from 'phaser';
import {
  TILE_SIZE,
  MAP_WIDTH,
  MAP_HEIGHT,
  MAP_COLS,
  MAP_ROWS,
  FARM_TILESET,
  FARM_TILES,
} from '../config/gameConfig';
import { DEPTH, getBuildingDepth, getCropDepth } from '../config/depthConfig';
import {
  CROPS,
  CROP_ASSET_PATH,
  getCropConfig,
  getCropFrame,
  getCropSpriteKey,
} from '../config/cropConfig';
import type { PlacedItem, ItemMetadata, FarmPlotData } from '@/lib/api/farm';

// 건물 에셋 경로
const BUILDING_PATH = '/farm/houses/';
const DECORATION_PATH = '/farm/decorations/';

// 스프라이트별 파일 매핑 (metadata.sprite → 실제 파일)
const SPRITE_FILES: Record<string, { file: string; frameWidth?: number; frameHeight?: number }> = {
  'buildings/house': { file: 'Farmer_House_1_32x32.png' },
  'buildings/well': { file: 'Well_Usable_Bucket_Full_32x32.png' },
  'buildings/chickenCoop': { file: 'Chicken_Coop_32x32.png' },
  'buildings/scarecrow': { file: 'Scarecrow_32x32.png' },
  'buildings/barn': { file: 'Barn_Small_32x32.png' },
  'trees/oak': { file: 'tree_oak.png' },
  'trees/pine': { file: 'tree_pine.png' },
  'trees/apple': { file: 'tree_apple.png' },
  'decorations/flower_red': { file: 'flower_red.png' },
  'decorations/flower_yellow': { file: 'flower_yellow.png' },
  'decorations/flower_purple': { file: 'flower_purple.png' },
  'decorations/grass': { file: 'grass.png' },
  'decorations/hay': { file: 'hay.png' },
  'decorations/rock': { file: 'rock.png' },
  'fences/wood': { file: 'fence_wood.png' },
  'fences/stone': { file: 'fence_stone.png' },
};

// 배치된 아이템 스프라이트 정보
interface PlacedItemSprite {
  item: PlacedItem;
  sprite: Phaser.GameObjects.Sprite;
  cropSprite?: Phaser.GameObjects.Sprite;  // 밭에 심은 작물
  timerText?: Phaser.GameObjects.Text;     // 성장 타이머
  originalX: number;
  originalY: number;
}

// 콜백 타입
type OnMoveCallback = (itemId: string, tileX: number, tileY: number) => void;
type OnRemoveCallback = (itemId: string) => void;
type OnPlantCallback = (plotId: string, cropCode: string) => void;
type OnHarvestCallback = (plotId: string) => void;

// 배치 변경 사항 타입
export interface PlacementChanges {
  moved: { id: string; tileX: number; tileY: number }[];
  deleted: string[];
  created: { tempId: string; itemCode: string; tileX: number; tileY: number }[];
}

// 임시 배치 아이템 (아직 DB에 없음)
interface PendingPlacement {
  tempId: string;
  itemCode: string;
  tileX: number;
  tileY: number;
  metadata: ItemMetadata;
}

export class UnifiedPlacementManager {
  private scene: Phaser.Scene;
  private placedItems: Map<string, PlacedItemSprite> = new Map();

  // 드래그 모드 상태
  private isDragMode: boolean = false;
  private draggedItem: PlacedItemSprite | null = null;
  private previewGraphics: Phaser.GameObjects.Graphics | null = null;
  private gridGraphics: Phaser.GameObjects.Graphics | null = null;

  // 밭 테두리 타일들 (9-patch)
  private farmBorderTiles: Phaser.GameObjects.Sprite[] = [];
  private farmPlotPositions: Set<string> = new Set();  // "x,y" 형식

  // 콜백
  private onMoveCallback: OnMoveCallback | null = null;
  private onRemoveCallback: OnRemoveCallback | null = null;
  private onPlantCallback: OnPlantCallback | null = null;
  private onHarvestCallback: OnHarvestCallback | null = null;

  // 로드된 에셋 키 추적
  private loadedAssets: Set<string> = new Set();

  // 타이머 업데이트
  private lastTimerUpdate: number = 0;

  // 배치 모드 스냅샷 및 변경 추적
  private placementSnapshot: Map<string, { tileX: number; tileY: number }> = new Map();
  private movedItems: Set<string> = new Set();
  private deletedItems: Map<string, PlacedItem> = new Map();  // id -> 삭제된 아이템 데이터
  private pendingPlacements: Map<string, PendingPlacement> = new Map();  // tempId -> 새 배치
  private tempIdCounter: number = 0;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드 (기본 에셋)
   */
  preload(): void {
    // 밭 타일 스프라이트시트 로드
    this.scene.load.spritesheet(
      FARM_TILESET.key,
      FARM_TILESET.path,
      {
        frameWidth: FARM_TILESET.frameWidth,
        frameHeight: FARM_TILESET.frameHeight,
      }
    );

    // 건물 에셋 로드
    Object.entries(SPRITE_FILES).forEach(([key, info]) => {
      const assetKey = this.getAssetKey(key);
      if (key.startsWith('buildings/')) {
        this.scene.load.image(assetKey, BUILDING_PATH + info.file);
      } else {
        this.scene.load.image(assetKey, DECORATION_PATH + info.file);
      }
      this.loadedAssets.add(assetKey);
    });

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
   * 초기화
   */
  create(): void {
    // 그리드 그래픽스 생성 (배치 모드에서 전체 맵에 표시)
    this.gridGraphics = this.scene.add.graphics();
    this.gridGraphics.setDepth(DEPTH.HIGHLIGHT - 1);
    this.gridGraphics.setVisible(false);

    // 미리보기 그래픽스 생성
    this.previewGraphics = this.scene.add.graphics();
    this.previewGraphics.setDepth(DEPTH.HIGHLIGHT);

    // 드래그 이벤트 설정
    this.setupDragEvents();
  }

  /**
   * 아이템 목록 로드
   */
  loadItems(items: PlacedItem[]): void {
    // 현재 드래그 모드 상태 저장
    const wasDragMode = this.isDragMode;

    // 진행 중인 드래그 취소 (스프라이트가 파괴되므로)
    if (this.draggedItem) {
      this.draggedItem = null;
      this.clearPreview();
    }

    // 기존 아이템 정리
    this.clearAllItems();

    // 1. farm_plot 위치 수집
    this.farmPlotPositions.clear();
    items.forEach(item => {
      if (item.itemCode === 'farm_plot') {
        this.farmPlotPositions.add(`${item.tileX},${item.tileY}`);
      }
    });

    // 2. 밭 테두리 렌더링 (9-patch)
    this.renderFarmBorders();

    // 3. 새 아이템 렌더링
    items.forEach(item => {
      this.renderItem(item);
    });

    // 드래그 모드였다면 다시 활성화
    if (wasDragMode) {
      this.enableDragMode();
    }
  }

  /**
   * 드래그 중인지 확인
   */
  isDragging(): boolean {
    return this.draggedItem !== null;
  }

  /**
   * 밭 테두리 렌더링 (9-patch 방식)
   * 인접한 farm_plot들의 외곽에 테두리 타일 배치
   */
  private renderFarmBorders(): void {
    // 기존 테두리 정리
    this.farmBorderTiles.forEach(tile => tile.destroy());
    this.farmBorderTiles = [];

    if (this.farmPlotPositions.size === 0) return;

    // 테두리 위치 계산
    const borderPositions = new Map<string, number>();  // "x,y" -> tileIndex

    this.farmPlotPositions.forEach(pos => {
      const [x, y] = pos.split(',').map(Number);

      // 8방향 체크 (상, 하, 좌, 우, 대각선)
      const directions = [
        { dx: -1, dy: -1, name: 'tl' },  // 좌상
        { dx: 0, dy: -1, name: 't' },    // 상
        { dx: 1, dy: -1, name: 'tr' },   // 우상
        { dx: -1, dy: 0, name: 'l' },    // 좌
        { dx: 1, dy: 0, name: 'r' },     // 우
        { dx: -1, dy: 1, name: 'bl' },   // 좌하
        { dx: 0, dy: 1, name: 'b' },     // 하
        { dx: 1, dy: 1, name: 'br' },    // 우하
      ];

      directions.forEach(({ dx, dy }) => {
        const nx = x + dx;
        const ny = y + dy;
        const neighborKey = `${nx},${ny}`;

        // 이웃에 farm_plot이 없으면 테두리 후보
        if (!this.farmPlotPositions.has(neighborKey)) {
          borderPositions.set(neighborKey, -1);  // 나중에 타일 종류 결정
        }
      });
    });

    // 각 테두리 위치의 타일 종류 결정
    borderPositions.forEach((_, key) => {
      const [x, y] = key.split(',').map(Number);
      const tileIndex = this.getBorderTileIndex(x, y);
      if (tileIndex !== -1) {
        borderPositions.set(key, tileIndex);
      }
    });

    // 테두리 타일 렌더링
    borderPositions.forEach((tileIndex, key) => {
      if (tileIndex === -1) return;  // 내부 타일 (CENTER와 겹침)

      const [x, y] = key.split(',').map(Number);
      const worldX = x * TILE_SIZE + TILE_SIZE / 2;
      const worldY = y * TILE_SIZE + TILE_SIZE / 2;

      const tile = this.scene.add.sprite(worldX, worldY, FARM_TILESET.key, tileIndex);
      tile.setDepth(DEPTH.SOIL_TILES - 1);  // 밭 CENTER보다 아래
      this.farmBorderTiles.push(tile);
    });
  }

  /**
   * 테두리 타일 종류 결정
   * 주변 farm_plot 위치에 따라 적절한 9-patch 타일 선택
   */
  private getBorderTileIndex(x: number, y: number): number {
    // 이 위치 주변에 farm_plot이 있는지 체크
    const hasTop = this.farmPlotPositions.has(`${x},${y - 1}`);
    const hasBottom = this.farmPlotPositions.has(`${x},${y + 1}`);
    const hasLeft = this.farmPlotPositions.has(`${x - 1},${y}`);
    const hasRight = this.farmPlotPositions.has(`${x + 1},${y}`);
    const hasTopLeft = this.farmPlotPositions.has(`${x - 1},${y - 1}`);
    const hasTopRight = this.farmPlotPositions.has(`${x + 1},${y - 1}`);
    const hasBottomLeft = this.farmPlotPositions.has(`${x - 1},${y + 1}`);
    const hasBottomRight = this.farmPlotPositions.has(`${x + 1},${y + 1}`);

    // 4방향 모두 farm_plot이면 이건 내부 → CENTER
    if (hasTop && hasBottom && hasLeft && hasRight) {
      return -1;  // 스킵 (실제 farm_plot이 그려짐)
    }

    // 모서리 (대각선 방향에만 farm_plot이 있는 경우)
    if (hasBottomRight && !hasBottom && !hasRight) return FARM_TILES.TOP_LEFT;
    if (hasBottomLeft && !hasBottom && !hasLeft) return FARM_TILES.TOP_RIGHT;
    if (hasTopRight && !hasTop && !hasRight) return FARM_TILES.BOTTOM_LEFT;
    if (hasTopLeft && !hasTop && !hasLeft) return FARM_TILES.BOTTOM_RIGHT;

    // 테두리 (한쪽 방향에 farm_plot이 있는 경우)
    if (hasBottom && !hasTop) return FARM_TILES.TOP;
    if (hasTop && !hasBottom) return FARM_TILES.BOTTOM;
    if (hasRight && !hasLeft) return FARM_TILES.LEFT;
    if (hasLeft && !hasRight) return FARM_TILES.RIGHT;

    // 안쪽 모서리 (두 방향에 farm_plot이 있는 경우)
    if (hasBottom && hasRight) return FARM_TILES.TOP_LEFT;
    if (hasBottom && hasLeft) return FARM_TILES.TOP_RIGHT;
    if (hasTop && hasRight) return FARM_TILES.BOTTOM_LEFT;
    if (hasTop && hasLeft) return FARM_TILES.BOTTOM_RIGHT;

    return -1;  // 해당 없음
  }

  /**
   * 개별 아이템 렌더링
   */
  private renderItem(item: PlacedItem): void {
    const assetKey = this.getAssetKey(item.metadata.sprite);
    const { width, height, depth } = item.metadata;

    // 월드 좌표 계산
    const worldX = item.tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
    const worldY = item.tileY * TILE_SIZE + height * TILE_SIZE;

    let sprite: Phaser.GameObjects.Sprite;

    // 밭인 경우 타일 스프라이트 사용
    if (item.itemCode === 'farm_plot') {
      sprite = this.renderFarmPlot(item);
    } else {
      // 일반 아이템
      sprite = this.scene.add.sprite(
        worldX,
        worldY,
        assetKey
      );
      sprite.setOrigin(0.5, 0.9);
    }

    // 깊이 설정 (Y 좌표 기반)
    const calculatedDepth = getBuildingDepth(worldY, MAP_HEIGHT);
    sprite.setDepth(calculatedDepth);

    // 데이터 저장
    sprite.setData('itemId', item.id);
    sprite.setData('itemCode', item.itemCode);

    const placedSprite: PlacedItemSprite = {
      item,
      sprite,
      originalX: item.tileX,
      originalY: item.tileY,
    };

    // 밭에 작물이 있으면 렌더링
    if (item.itemCode === 'farm_plot') {
      const data = item.data as FarmPlotData;
      if (data.cropCode) {
        this.renderCropOnPlot(placedSprite, data);
      }
    }

    this.placedItems.set(item.id, placedSprite);
  }

  /**
   * 밭 타일 렌더링
   */
  private renderFarmPlot(item: PlacedItem): Phaser.GameObjects.Sprite {
    const worldX = item.tileX * TILE_SIZE + TILE_SIZE / 2;
    const worldY = item.tileY * TILE_SIZE + TILE_SIZE / 2;

    // 밭 중앙 타일 사용
    const sprite = this.scene.add.sprite(worldX, worldY, FARM_TILESET.key, FARM_TILES.CENTER);
    sprite.setDepth(DEPTH.SOIL_TILES);

    return sprite;
  }

  /**
   * 밭 위에 작물 렌더링
   */
  private renderCropOnPlot(placedSprite: PlacedItemSprite, data: FarmPlotData): void {
    if (!data.cropCode) return;

    const cropConfig = getCropConfig(data.cropCode);
    if (!cropConfig) return;

    const { item, sprite } = placedSprite;
    const worldX = item.tileX * TILE_SIZE + TILE_SIZE / 2;
    const worldY = item.tileY * TILE_SIZE + TILE_SIZE / 2;

    // 성장 단계 계산
    const stage = data.stage || 0;
    const frame = getCropFrame(data.cropCode, stage);

    // 작물 스프라이트 생성
    const cropSprite = this.scene.add.sprite(
      worldX,
      worldY,
      getCropSpriteKey(data.cropCode),
      frame
    );
    cropSprite.setDepth(getCropDepth(worldY, MAP_HEIGHT));

    placedSprite.cropSprite = cropSprite;

    // 타이머 텍스트 (stage < 4일 때)
    if (stage < 4 && data.plantedAt) {
      const timerText = this.scene.add.text(worldX, worldY - 20, '', {
        fontSize: '10px',
        color: '#ffffff',
        stroke: '#000000',
        strokeThickness: 2,
      });
      timerText.setOrigin(0.5, 1);
      timerText.setDepth(DEPTH.OVERLAY);
      placedSprite.timerText = timerText;
    }
  }

  /**
   * 작물 업데이트 (stage 변경)
   */
  updateCrop(plotId: string, cropCode: string | null, stage: number): void {
    const placed = this.placedItems.get(plotId);
    if (!placed) return;

    // 기존 작물 스프라이트 제거
    if (placed.cropSprite) {
      placed.cropSprite.destroy();
      placed.cropSprite = undefined;
    }
    if (placed.timerText) {
      placed.timerText.destroy();
      placed.timerText = undefined;
    }

    // 새 작물 렌더링
    if (cropCode) {
      const data: FarmPlotData = {
        cropCode,
        stage,
        plantedAt: new Date().toISOString(),
      };
      this.renderCropOnPlot(placed, data);
    }

    // item 데이터 업데이트
    placed.item.data = cropCode
      ? { cropCode, stage, plantedAt: placed.item.data?.plantedAt || new Date().toISOString() }
      : {};
  }

  /**
   * 매 프레임 업데이트 (타이머 갱신)
   */
  update(): void {
    const now = Date.now();
    if (now - this.lastTimerUpdate < 1000) return;
    this.lastTimerUpdate = now;

    this.placedItems.forEach(placed => {
      if (placed.item.itemCode !== 'farm_plot') return;

      const data = placed.item.data as FarmPlotData;
      if (!data.cropCode || !data.plantedAt) return;

      const cropConfig = getCropConfig(data.cropCode);
      if (!cropConfig) return;

      // 성장 시간 계산 (기본 120초)
      const plantedAt = new Date(data.plantedAt).getTime();
      const growTimeSeconds = (placed.item.data as FarmPlotData & { growTimeSeconds?: number }).growTimeSeconds || 120;
      const growTimeMs = growTimeSeconds * 1000;
      const elapsed = now - plantedAt;
      const remaining = Math.max(0, growTimeMs - elapsed);

      // 완료됐으면 타이머 숨기기
      if (remaining <= 0) {
        if (placed.timerText) {
          placed.timerText.setVisible(false);
        }
        return;
      }

      // 타이머 텍스트 업데이트
      if (placed.timerText) {
        const seconds = Math.ceil(remaining / 1000);
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        placed.timerText.setText(`${min}:${sec.toString().padStart(2, '0')}`);
        placed.timerText.setVisible(true);
      }
    });
  }

  /**
   * 드래그 이벤트 설정
   */
  private setupDragEvents(): void {
    this.scene.input.on('dragstart', (pointer: Phaser.Input.Pointer, gameObject: Phaser.GameObjects.Sprite) => {
      if (!this.isDragMode) return;

      const itemId = gameObject.getData('itemId');
      const placed = this.placedItems.get(itemId);

      if (placed && placed.item.metadata.canMove) {
        this.draggedItem = placed;
        placed.originalX = placed.item.tileX;
        placed.originalY = placed.item.tileY;

        gameObject.setAlpha(0.7);
        gameObject.setDepth(DEPTH.HIGHLIGHT + 10);
      }
    });

    this.scene.input.on('drag', (pointer: Phaser.Input.Pointer, gameObject: Phaser.GameObjects.Sprite, dragX: number, dragY: number) => {
      if (!this.isDragMode || !this.draggedItem) return;

      const { width, height } = this.draggedItem.item.metadata;

      // 그리드 스냅
      const tileX = Math.floor(dragX / TILE_SIZE) - Math.floor(width / 2);
      const tileY = Math.floor(dragY / TILE_SIZE) - Math.floor(height / 2);

      // 스프라이트 이동
      const previewWorldX = tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
      const previewWorldY = tileY * TILE_SIZE + height * TILE_SIZE;
      gameObject.setPosition(previewWorldX, previewWorldY);

      // 미리보기
      const isValid = this.canPlaceAt(this.draggedItem.item.id, tileX, tileY, width, height);
      this.drawPreview(tileX, tileY, width, height, isValid);
    });

    this.scene.input.on('dragend', (pointer: Phaser.Input.Pointer, gameObject: Phaser.GameObjects.Sprite) => {
      if (!this.isDragMode || !this.draggedItem) return;

      const { width, height } = this.draggedItem.item.metadata;

      // 최종 위치 계산
      const worldX = gameObject.x;
      const worldY = gameObject.y;
      const tileX = Math.floor((worldX - (width * TILE_SIZE) / 2) / TILE_SIZE);
      const tileY = Math.floor((worldY - height * TILE_SIZE) / TILE_SIZE);

      const isValid = this.canPlaceAt(this.draggedItem.item.id, tileX, tileY, width, height);

      if (isValid) {
        // 새 위치 적용 (로컬에서만)
        this.draggedItem.item.tileX = tileX;
        this.draggedItem.item.tileY = tileY;

        const finalWorldX = tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
        const finalWorldY = tileY * TILE_SIZE + height * TILE_SIZE;
        gameObject.setPosition(finalWorldX, finalWorldY);

        const depth = getBuildingDepth(finalWorldY, MAP_HEIGHT);
        gameObject.setDepth(depth);

        // 밭이면 작물 스프라이트도 이동
        const placed = this.placedItems.get(this.draggedItem.item.id);
        if (placed && placed.item.itemCode === 'farm_plot') {
          const cropWorldX = tileX * TILE_SIZE + TILE_SIZE / 2;
          const cropWorldY = tileY * TILE_SIZE + TILE_SIZE / 2;
          if (placed.cropSprite) {
            placed.cropSprite.setPosition(cropWorldX, cropWorldY);
          }
          if (placed.timerText) {
            placed.timerText.setPosition(cropWorldX, cropWorldY - 20);
          }
        }

        // 변경 추적 (API 호출하지 않음)
        this.movedItems.add(this.draggedItem.item.id);
      } else {
        // 원래 위치로 복귀
        const originalWorldX = this.draggedItem.originalX * TILE_SIZE + (width * TILE_SIZE) / 2;
        const originalWorldY = this.draggedItem.originalY * TILE_SIZE + height * TILE_SIZE;
        gameObject.setPosition(originalWorldX, originalWorldY);

        this.draggedItem.item.tileX = this.draggedItem.originalX;
        this.draggedItem.item.tileY = this.draggedItem.originalY;

        const depth = getBuildingDepth(originalWorldY, MAP_HEIGHT);
        gameObject.setDepth(depth);
      }

      gameObject.setAlpha(1);
      this.draggedItem = null;
      this.clearPreview();
    });
  }

  /**
   * 배치 가능 여부 확인 (오버로드 버전)
   */
  canPlaceAt(tileX: number, tileY: number, width: number, height: number): boolean;
  canPlaceAt(excludeId: string, tileX: number, tileY: number, width: number, height: number): boolean;
  canPlaceAt(
    arg1: string | number,
    arg2: number,
    arg3: number,
    arg4: number,
    arg5?: number
  ): boolean {
    let excludeId: string = '';
    let tileX: number;
    let tileY: number;
    let width: number;
    let height: number;

    if (typeof arg1 === 'string') {
      // 5-param version: excludeId, tileX, tileY, width, height
      excludeId = arg1;
      tileX = arg2;
      tileY = arg3;
      width = arg4;
      height = arg5!;
    } else {
      // 4-param version: tileX, tileY, width, height
      tileX = arg1;
      tileY = arg2;
      width = arg3;
      height = arg4;
    }

    // 맵 범위 체크
    if (tileX < 0 || tileX + width > MAP_COLS || tileY < 0 || tileY + height > MAP_ROWS) {
      return false;
    }

    // 다른 아이템과 충돌 체크
    for (const [id, placed] of Array.from(this.placedItems.entries())) {
      if (id === excludeId) continue;

      const { item } = placed;
      const { width: otherWidth, height: otherHeight } = item.metadata;

      // AABB 충돌
      if (tileX < item.tileX + otherWidth &&
          tileX + width > item.tileX &&
          tileY < item.tileY + otherHeight &&
          tileY + height > item.tileY) {
        return false;
      }
    }

    return true;
  }

  /**
   * 미리보기 그리기
   */
  private drawPreview(tileX: number, tileY: number, width: number, height: number, isValid: boolean): void {
    if (!this.previewGraphics) return;

    this.previewGraphics.clear();

    const x = tileX * TILE_SIZE;
    const y = tileY * TILE_SIZE;
    const w = width * TILE_SIZE;
    const h = height * TILE_SIZE;

    const fillColor = isValid ? 0x00ff00 : 0xff0000;
    this.previewGraphics.fillStyle(fillColor, 0.3);
    this.previewGraphics.fillRect(x, y, w, h);

    this.previewGraphics.lineStyle(2, fillColor, 0.8);
    this.previewGraphics.strokeRect(x, y, w, h);
  }

  /**
   * 미리보기 지우기
   */
  private clearPreview(): void {
    if (this.previewGraphics) {
      this.previewGraphics.clear();
    }
  }

  /**
   * 전체 맵 격자무늬 표시
   */
  private showGrid(): void {
    if (!this.gridGraphics) return;

    this.gridGraphics.clear();
    this.gridGraphics.lineStyle(1, 0xffffff, 0.15);

    // 세로선
    for (let col = 0; col <= MAP_COLS; col++) {
      this.gridGraphics.lineBetween(
        col * TILE_SIZE, 0,
        col * TILE_SIZE, MAP_HEIGHT
      );
    }

    // 가로선
    for (let row = 0; row <= MAP_ROWS; row++) {
      this.gridGraphics.lineBetween(
        0, row * TILE_SIZE,
        MAP_WIDTH, row * TILE_SIZE
      );
    }

    this.gridGraphics.setVisible(true);
  }

  /**
   * 격자무늬 숨기기
   */
  private hideGrid(): void {
    if (this.gridGraphics) {
      this.gridGraphics.setVisible(false);
    }
  }

  /**
   * 드래그 모드 활성화
   */
  enableDragMode(): void {
    this.isDragMode = true;

    // 스냅샷 저장 (배치 모드 진입 시 현재 상태 저장)
    this.placementSnapshot.clear();
    this.movedItems.clear();
    this.deletedItems.clear();

    this.placedItems.forEach((placed, id) => {
      this.placementSnapshot.set(id, {
        tileX: placed.item.tileX,
        tileY: placed.item.tileY,
      });
    });

    // 격자무늬 표시
    this.showGrid();

    this.placedItems.forEach(placed => {
      if (placed.item.metadata.canMove) {
        placed.sprite.setInteractive({ draggable: true });
        placed.sprite.setTint(0xaaaaff);
      }
    });
  }

  /**
   * 드래그 모드 비활성화
   */
  disableDragMode(): void {
    this.isDragMode = false;

    // 격자무늬 숨기기
    this.hideGrid();

    this.placedItems.forEach(placed => {
      placed.sprite.disableInteractive();
      placed.sprite.clearTint();
    });

    this.clearPreview();
    this.draggedItem = null;
  }

  /**
   * 변경 사항이 있는지 확인
   */
  hasChanges(): boolean {
    // 이동된 아이템 중 실제로 위치가 변경된 것이 있는지 확인
    for (const id of Array.from(this.movedItems)) {
      const placed = this.placedItems.get(id);
      const snapshot = this.placementSnapshot.get(id);
      if (placed && snapshot) {
        if (placed.item.tileX !== snapshot.tileX || placed.item.tileY !== snapshot.tileY) {
          return true;
        }
      }
    }
    // 삭제된 아이템이 있는지 확인
    return this.deletedItems.size > 0;
  }

  /**
   * 변경 사항 가져오기
   */
  getChanges(): PlacementChanges {
    const moved: { id: string; tileX: number; tileY: number }[] = [];
    const created: { tempId: string; itemCode: string; tileX: number; tileY: number }[] = [];

    // 이동된 아이템 중 실제로 위치가 변경된 것만 추출
    for (const id of Array.from(this.movedItems)) {
      // 임시 배치는 제외 (created에서 처리)
      if (this.pendingPlacements.has(id)) continue;

      const placed = this.placedItems.get(id);
      const snapshot = this.placementSnapshot.get(id);
      if (placed && snapshot) {
        if (placed.item.tileX !== snapshot.tileX || placed.item.tileY !== snapshot.tileY) {
          moved.push({
            id,
            tileX: placed.item.tileX,
            tileY: placed.item.tileY,
          });
        }
      }
    }

    // 새로 배치된 아이템 (현재 위치로)
    for (const [tempId, pending] of Array.from(this.pendingPlacements.entries())) {
      // 현재 위치 가져오기 (드래그로 이동했을 수 있음)
      const placed = this.placedItems.get(tempId);
      const currentX = placed?.item.tileX ?? pending.tileX;
      const currentY = placed?.item.tileY ?? pending.tileY;

      created.push({
        tempId,
        itemCode: pending.itemCode,
        tileX: currentX,
        tileY: currentY,
      });
    }

    return {
      moved,
      deleted: Array.from(this.deletedItems.keys()),
      created,
    };
  }

  /**
   * 변경 사항 취소 (스냅샷으로 복원)
   */
  revertChanges(): void {
    // 임시 배치 제거 (새로 배치한 것들)
    for (const [tempId, pending] of Array.from(this.pendingPlacements.entries())) {
      const placed = this.placedItems.get(tempId);
      if (placed) {
        placed.sprite.destroy();
        if (placed.cropSprite) placed.cropSprite.destroy();
        if (placed.timerText) placed.timerText.destroy();
        this.placedItems.delete(tempId);

        // 밭이면 위치 제거
        if (pending.itemCode === 'farm_plot') {
          this.farmPlotPositions.delete(`${placed.item.tileX},${placed.item.tileY}`);
        }
      }
    }

    // 이동된 아이템 복원
    for (const id of Array.from(this.movedItems)) {
      // 임시 배치는 이미 위에서 처리됨
      if (this.pendingPlacements.has(id)) continue;

      const placed = this.placedItems.get(id);
      const snapshot = this.placementSnapshot.get(id);

      if (placed && snapshot) {
        // 위치 복원
        placed.item.tileX = snapshot.tileX;
        placed.item.tileY = snapshot.tileY;

        // 스프라이트 위치 복원
        const { width, height } = placed.item.metadata;
        if (placed.item.itemCode === 'farm_plot') {
          const worldX = snapshot.tileX * TILE_SIZE + TILE_SIZE / 2;
          const worldY = snapshot.tileY * TILE_SIZE + TILE_SIZE / 2;
          placed.sprite.setPosition(worldX, worldY);
          if (placed.cropSprite) {
            placed.cropSprite.setPosition(worldX, worldY);
          }
          if (placed.timerText) {
            placed.timerText.setPosition(worldX, worldY - 20);
          }
        } else {
          const worldX = snapshot.tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
          const worldY = snapshot.tileY * TILE_SIZE + height * TILE_SIZE;
          placed.sprite.setPosition(worldX, worldY);
          const depth = getBuildingDepth(worldY, MAP_HEIGHT);
          placed.sprite.setDepth(depth);
        }
      }
    }

    // 삭제된 아이템 복원
    for (const [id, item] of Array.from(this.deletedItems.entries())) {
      this.renderItem(item);
      // 드래그 모드 상태로 복원
      const placed = this.placedItems.get(id);
      if (placed && placed.item.metadata.canMove) {
        placed.sprite.setInteractive({ draggable: true });
        placed.sprite.setTint(0xaaaaff);
      }
    }

    // 밭 테두리 재렌더링
    this.farmPlotPositions.clear();
    this.placedItems.forEach((placed) => {
      if (placed.item.itemCode === 'farm_plot') {
        this.farmPlotPositions.add(`${placed.item.tileX},${placed.item.tileY}`);
      }
    });
    this.renderFarmBorders();

    // 변경 추적 초기화
    this.movedItems.clear();
    this.deletedItems.clear();
    this.pendingPlacements.clear();
  }

  /**
   * 아이템 로컬 삭제 (배치 모드에서만 사용)
   * 실제 API는 호출하지 않고 변경 추적만 함
   */
  deleteItemLocally(itemId: string): boolean {
    // 임시 배치인 경우 (아직 DB에 없음)
    if (this.pendingPlacements.has(itemId)) {
      const pending = this.pendingPlacements.get(itemId)!;
      const placed = this.placedItems.get(itemId);

      if (placed) {
        placed.sprite.destroy();
        if (placed.cropSprite) placed.cropSprite.destroy();
        if (placed.timerText) placed.timerText.destroy();
        this.placedItems.delete(itemId);

        // 밭이면 테두리 재렌더링
        if (pending.itemCode === 'farm_plot') {
          this.farmPlotPositions.delete(`${pending.tileX},${pending.tileY}`);
          this.renderFarmBorders();
        }
      }

      this.pendingPlacements.delete(itemId);
      return true;
    }

    // 기존 아이템인 경우 (DB에 있음)
    const placed = this.placedItems.get(itemId);
    if (!placed) return false;

    // 삭제 불가능한 아이템 체크
    if (!placed.item.metadata.canDelete) {
      return false;
    }

    // 삭제된 아이템 저장 (복원용)
    this.deletedItems.set(itemId, { ...placed.item });

    // 스프라이트 제거
    placed.sprite.destroy();
    if (placed.cropSprite) placed.cropSprite.destroy();
    if (placed.timerText) placed.timerText.destroy();
    this.placedItems.delete(itemId);

    // 밭이면 테두리 재렌더링
    if (placed.item.itemCode === 'farm_plot') {
      this.farmPlotPositions.delete(`${placed.item.tileX},${placed.item.tileY}`);
      this.renderFarmBorders();
    }

    return true;
  }

  /**
   * 아이템 로컬 배치 (배치 모드에서만 사용)
   * 실제 API는 호출하지 않고 로컬에서만 렌더링
   * @returns tempId 또는 null (배치 실패 시)
   */
  placeItemLocally(itemCode: string, tileX: number, tileY: number, metadata: ItemMetadata): string | null {
    const { width, height } = metadata;

    // 배치 가능 여부 확인
    if (!this.canPlaceAt(tileX, tileY, width, height)) {
      return null;
    }

    // 임시 ID 생성
    const tempId = `temp_${Date.now()}_${this.tempIdCounter++}`;

    // PlacedItem 생성 (임시)
    const placedItem: PlacedItem = {
      id: tempId,
      itemCode,
      tileX,
      tileY,
      rotation: 0,
      metadata,
      data: {},
    };

    // 스프라이트 렌더링
    this.renderItem(placedItem);

    // 드래그 모드 상태로 설정
    const placed = this.placedItems.get(tempId);
    if (placed && metadata.canMove) {
      placed.sprite.setInteractive({ draggable: true });
      placed.sprite.setTint(0xaaaaff);
    }

    // 밭이면 테두리 재렌더링
    if (itemCode === 'farm_plot') {
      this.farmPlotPositions.add(`${tileX},${tileY}`);
      this.renderFarmBorders();
    }

    // 임시 배치 추적
    this.pendingPlacements.set(tempId, {
      tempId,
      itemCode,
      tileX,
      tileY,
      metadata,
    });

    return tempId;
  }

  /**
   * 변경 사항 확정 후 초기화
   */
  clearChanges(): void {
    this.placementSnapshot.clear();
    this.movedItems.clear();
    this.deletedItems.clear();
    this.pendingPlacements.clear();
  }

  /**
   * 아이템 추가
   */
  addItem(item: PlacedItem): void {
    this.renderItem(item);

    // 드래그 모드라면 새 아이템도 드래그 가능하게
    if (this.isDragMode) {
      const placed = this.placedItems.get(item.id);
      if (placed && placed.item.metadata.canMove) {
        placed.sprite.setInteractive({ draggable: true });
        placed.sprite.setTint(0xaaaaff);
      }
    }
  }

  /**
   * 아이템 제거
   */
  removeItem(itemId: string): boolean {
    const placed = this.placedItems.get(itemId);
    if (!placed) return false;

    placed.sprite.destroy();
    if (placed.cropSprite) placed.cropSprite.destroy();
    if (placed.timerText) placed.timerText.destroy();

    this.placedItems.delete(itemId);
    return true;
  }

  /**
   * 아이템 이동 (외부에서 호출)
   */
  moveItem(itemId: string, tileX: number, tileY: number): void {
    const placed = this.placedItems.get(itemId);
    if (!placed) return;

    placed.item.tileX = tileX;
    placed.item.tileY = tileY;

    const { width, height } = placed.item.metadata;
    const worldX = tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
    const worldY = tileY * TILE_SIZE + height * TILE_SIZE;

    placed.sprite.setPosition(worldX, worldY);

    const depth = getBuildingDepth(worldY, MAP_HEIGHT);
    placed.sprite.setDepth(depth);
  }

  /**
   * 특정 위치의 아이템 찾기
   */
  getItemAt(tileX: number, tileY: number): PlacedItem | null {
    for (const [, placed] of Array.from(this.placedItems.entries())) {
      const { item } = placed;
      const { width, height } = item.metadata;

      if (tileX >= item.tileX && tileX < item.tileX + width &&
          tileY >= item.tileY && tileY < item.tileY + height) {
        return item;
      }
    }
    return null;
  }

  /**
   * 밭(farm_plot) 찾기
   */
  getFarmPlotAt(tileX: number, tileY: number): PlacedItem | null {
    const item = this.getItemAt(tileX, tileY);
    if (item && item.itemCode === 'farm_plot') {
      return item;
    }
    return null;
  }

  /**
   * 모든 아이템 가져오기
   */
  getPlacedItems(): PlacedItem[] {
    return Array.from(this.placedItems.values()).map(p => p.item);
  }

  /**
   * 모든 밭(farm_plot) 가져오기
   */
  getFarmPlots(): PlacedItem[] {
    return Array.from(this.placedItems.values())
      .filter(p => p.item.itemCode === 'farm_plot')
      .map(p => p.item);
  }

  /**
   * 에셋 키 생성
   */
  private getAssetKey(sprite: string): string {
    return `item_${sprite.replace(/\//g, '_')}`;
  }

  /**
   * 콜백 설정 (객체 형태)
   */
  setCallbacks(callbacks: {
    onMoveItem?: (itemId: string, tileX: number, tileY: number) => Promise<void>;
    onRemoveItem?: (itemId: string) => Promise<void>;
    onPlantOnPlot?: (plotId: string, cropCode: string) => Promise<void>;
    onHarvestFromPlot?: (plotId: string) => Promise<{ gold: number; xp: number } | null>;
  }): void {
    if (callbacks.onMoveItem) {
      this.onMoveCallback = (itemId, tileX, tileY) => {
        callbacks.onMoveItem!(itemId, tileX, tileY);
      };
    }
    if (callbacks.onRemoveItem) {
      this.onRemoveCallback = (itemId) => {
        callbacks.onRemoveItem!(itemId);
      };
    }
    if (callbacks.onPlantOnPlot) {
      this.onPlantCallback = (plotId, cropCode) => {
        callbacks.onPlantOnPlot!(plotId, cropCode);
      };
    }
    if (callbacks.onHarvestFromPlot) {
      this.onHarvestCallback = (plotId) => {
        callbacks.onHarvestFromPlot!(plotId);
      };
    }
  }

  /**
   * 모든 아이템 정리
   */
  private clearAllItems(): void {
    // 배치된 아이템 정리
    this.placedItems.forEach(placed => {
      placed.sprite.destroy();
      if (placed.cropSprite) placed.cropSprite.destroy();
      if (placed.timerText) placed.timerText.destroy();
    });
    this.placedItems.clear();

    // 밭 테두리 정리
    this.farmBorderTiles.forEach(tile => tile.destroy());
    this.farmBorderTiles = [];
    this.farmPlotPositions.clear();
  }

  /**
   * 정리
   */
  destroy(): void {
    this.clearAllItems();

    if (this.previewGraphics) {
      this.previewGraphics.destroy();
      this.previewGraphics = null;
    }

    if (this.gridGraphics) {
      this.gridGraphics.destroy();
      this.gridGraphics = null;
    }
  }
}
