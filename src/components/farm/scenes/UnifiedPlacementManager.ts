/**
 * UnifiedPlacementManager - 통합 배치 시스템
 * 건물, 나무, 장식, 울타리 등 배치 가능 아이템 관리
 *
 * 참고: 밭(farm_plot)은 FarmGridManager에서 별도로 관리
 */

import * as Phaser from 'phaser';
import {
  TILE_SIZE,
  MAP_WIDTH,
  MAP_HEIGHT,
  MAP_COLS,
  MAP_ROWS,
} from '../config/gameConfig';
import { DEPTH, getBuildingDepth } from '../config/depthConfig';
import type { PlacedItem, ItemMetadata } from '@/lib/api/farm';

// 에셋 경로 (기본 경로)
const FARM_BASE_PATH = '/farm/';

// 스프라이트별 파일 매핑 (metadata.sprite → 실제 파일)
// path: 하위 폴더, file: 파일명
const SPRITE_FILES: Record<string, { path: string; file: string; frameWidth?: number; frameHeight?: number }> = {
  // 건물 (houses/)
  'buildings/house': { path: 'houses/', file: 'Farmer_House_1_32x32.png' },
  'buildings/well': { path: 'houses/', file: 'Well_Usable_Bucket_Full_32x32.png' },
  'buildings/chickenCoop': { path: 'houses/', file: 'Chicken_Coop_32x32.png' },
  'buildings/chicken_coop': { path: 'houses/', file: 'Chicken_Coop_32x32.png' },  // DB 호환
  'buildings/scarecrow': { path: 'houses/', file: 'Scarecrow_32x32.png' },
  'buildings/barn': { path: 'houses/', file: 'Barn_Small_32x32.png' },

  // 새 건물 (houses/)
  'buildings/farmer_house_1': { path: 'houses/', file: 'Farmer_House_1_32x32.png' },
  'buildings/farmer_house_2': { path: 'houses/', file: 'Farmer_House_2_32x32.png' },
  'buildings/barn_small': { path: 'houses/', file: 'Barn_Small_32x32.png' },
  'buildings/stable': { path: 'houses/', file: 'Stable_Example_Outside_32x32.png' },
  'buildings/silos': { path: 'houses/', file: 'Silos_1_32x32.png' },
  'buildings/doghouse': { path: 'houses/', file: 'Doghouse_32x32.png' },

  // 작업대 (houses/)
  'buildings/stone_oven': { path: 'houses/', file: 'Stone_Oven_1_32x32.png' },
  'buildings/cheese_machine': { path: 'houses/', file: 'Cheese_Machine_Full_32x32.png' },
  'buildings/diy_crafting_table': { path: 'houses/', file: 'DIY_Crafting_Table_32x32.png' },
  'buildings/tailor_table': { path: 'houses/', file: 'Tailor_Crafting_Table_32x32.png' },
  'buildings/woodwork_table': { path: 'houses/', file: 'Woodwork_Crafting_Table_32x32.png' },

  // 마켓 가판대 (houses/)
  'buildings/market_stand_blue': { path: 'houses/', file: 'Market_Stand_Blue_Big_32x32.png' },
  'buildings/market_stand_green': { path: 'houses/', file: 'Market_Stand_Green_Big_32x32.png' },
  'buildings/market_stand_yellow': { path: 'houses/', file: 'Market_Stand_Yellow_Big_32x32.png' },
  'buildings/market_stand_pink': { path: 'houses/', file: 'Market_Stand_Pink_Big_32x32.png' },

  // 나무 - 애니메이션 GIF (animated/)
  'trees/oak': { path: 'animated/', file: 'Trees_Oak_Green_Big_Shake_32x32.gif' },
  'trees/oak_small': { path: 'animated/', file: 'Trees_Oak_Green_Small_Shake_32x32.gif' },
  'trees/oak_medium': { path: 'animated/', file: 'Trees_Oak_Green_Medium_Shake_32x32.gif' },
  'trees/pine': { path: 'animated/', file: 'Trees_Pine_Green_Big_Shake_32x32.gif' },
  'trees/pine_small': { path: 'animated/', file: 'Trees_Pine_Green_Small_Shake_32x32.gif' },
  'trees/pine_medium': { path: 'animated/', file: 'Trees_Pine_Green_Medium_Shake_32x32.gif' },
  'trees/apple': { path: 'animated/', file: 'Fruit_Tree_Apple_Ripe_Shake_32x32.gif' },
  'trees/birch': { path: 'animated/', file: 'Trees_Birch_Green_Big_Shake_32x32.gif' },

  // 꽃 (terrains/)
  'decorations/flower_blue': { path: 'terrains/', file: 'Flower_Blue_32x32.png' },
  'decorations/flower_pink': { path: 'terrains/', file: 'Flower_Pink_32x32.png' },
  'decorations/flower_yellow': { path: 'terrains/', file: 'Flower_Yellow_32x32.png' },
  'decorations/flower_green': { path: 'terrains/', file: 'Flower_Green_32x32.png' },

  // 잔디 (terrains/)
  'decorations/grass_1': { path: 'terrains/', file: 'Grass_Tufts_Flowers_32x32_1.png' },
  'decorations/grass_2': { path: 'terrains/', file: 'Grass_Tufts_Flowers_32x32_2.png' },
  'decorations/grass_3': { path: 'terrains/', file: 'Grass_Tufts_Flowers_32x32_3.png' },

  // 건초 (terrains/)
  'decorations/hay': { path: 'terrains/', file: 'Hay_Dry_Pile_32x32.png' },
  'decorations/hay_pile': { path: 'terrains/', file: 'Hay_Fresh_Pile_32x32.png' },
  'decorations/hay_small': { path: 'terrains/', file: 'Hay_Fresh_Pile_Small_32x32.png' },

  // 울타리 - 개별 추출된 파일
  'fences/wood': { path: 'terrains/', file: 'fence_wood_horizontal.png' },
  'fences/brown': { path: 'terrains/', file: 'fence_brown_32x32.png' },
  'fences/wood_horizontal': { path: 'terrains/', file: 'fence_wood_horizontal.png' },
  'fences/wood_vertical': { path: 'terrains/', file: 'fence_wood_vertical.png' },
  'fences/wood_corner': { path: 'terrains/', file: 'fence_wood_corner_tl.png' },
  'fences/post': { path: 'terrains/', file: 'fence_post_horizontal.png' },
  'fences/post_horizontal': { path: 'terrains/', file: 'fence_post_horizontal.png' },
  'fences/post_vertical': { path: 'terrains/', file: 'fence_post_vertical.png' },
  'fences/post_corner': { path: 'terrains/', file: 'fence_post_corner.png' },
  'fences/metal': { path: 'terrains/', file: 'fence_metal_horizontal.png' },
  'fences/metal_horizontal': { path: 'terrains/', file: 'fence_metal_horizontal.png' },
  'fences/metal_vertical': { path: 'terrains/', file: 'fence_metal_vertical.png' },

  // 바위 (terrains/)
  'decorations/rock_small': { path: 'terrains/', file: 'Rock_Small_32x32.png' },
  'decorations/rock_medium': { path: 'terrains/', file: 'Rock_Medium_32x32.png' },

  // 소품 (terrains/)
  'decorations/bucket': { path: 'terrains/', file: 'Bucket_32x32.png' },
  'decorations/crate': { path: 'terrains/', file: 'Crate_32x32.png' },
  'decorations/sign_chicken': { path: 'terrains/', file: 'Sign_Chicken_32x32.png' },
};

// 배치된 아이템 스프라이트 정보
interface PlacedItemSprite {
  item: PlacedItem;
  sprite: Phaser.GameObjects.Sprite;
  originalX: number;
  originalY: number;
}

// 콜백 타입
type OnMoveCallback = (itemId: string, tileX: number, tileY: number) => void;
type OnRemoveCallback = (itemId: string) => void;

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

  // 동적 맵 크기 (기본값은 상수 사용)
  private mapCols: number = MAP_COLS;
  private mapRows: number = MAP_ROWS;

  // 드래그 모드 상태
  private isDragMode: boolean = false;
  private draggedItem: PlacedItemSprite | null = null;
  private previewGraphics: Phaser.GameObjects.Graphics | null = null;
  private gridGraphics: Phaser.GameObjects.Graphics | null = null;

  // 콜백
  private onMoveCallback: OnMoveCallback | null = null;
  private onRemoveCallback: OnRemoveCallback | null = null;

  // 로드된 에셋 키 추적
  private loadedAssets: Set<string> = new Set();

  // 충돌 디버그 시각화
  private collisionDebugGraphics: Phaser.GameObjects.Graphics | null = null;
  private collisionDebugVisible: boolean = false;

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
   * 맵 크기 설정 (동적 맵 확장용)
   */
  setMapBounds(cols: number, rows: number): void {
    this.mapCols = cols;
    this.mapRows = rows;
  }

  /**
   * 에셋 프리로드 (지연 로딩 적용)
   * 배치된 아이템만 로드하여 초기 로딩 시간 단축
   * @param placedItems 현재 배치된 아이템 목록
   */
  preload(placedItems?: PlacedItem[]): void {
    // 필요한 스프라이트만 추출
    const neededSprites = new Set<string>();

    // 기본 건물 (항상 로드 - 초기 배치 아이템)
    // chicken_coop: DB에서 스네이크케이스로 저장됨
    const defaultSprites = ['buildings/house', 'buildings/well', 'buildings/chicken_coop', 'buildings/scarecrow'];
    defaultSprites.forEach(s => neededSprites.add(s));

    // 배치된 아이템의 스프라이트
    if (placedItems) {
      placedItems.forEach(item => {
        if (item.itemCode !== 'farm_plot' && item.metadata?.sprite) {
          neededSprites.add(item.metadata.sprite);
        }
      });
    }

    console.log('[UnifiedPlacementManager] Loading sprites:', neededSprites.size, '/', Object.keys(SPRITE_FILES).length);

    // 필요한 에셋만 로드
    neededSprites.forEach(spriteKey => {
      const info = SPRITE_FILES[spriteKey];
      if (!info) return;

      const assetKey = this.getAssetKey(spriteKey);
      if (!this.scene.textures.exists(assetKey)) {
        const fullPath = FARM_BASE_PATH + info.path + info.file;
        this.scene.load.image(assetKey, fullPath);
      }
      this.loadedAssets.add(assetKey);
    });
  }

  /**
   * 런타임 중 에셋 로드 (새 아이템 배치 시)
   */
  loadAsset(spriteKey: string): Promise<void> {
    return new Promise((resolve) => {
      const info = SPRITE_FILES[spriteKey];
      if (!info) {
        resolve();
        return;
      }

      const assetKey = this.getAssetKey(spriteKey);
      if (this.scene.textures.exists(assetKey)) {
        resolve();
        return;
      }

      const fullPath = FARM_BASE_PATH + info.path + info.file;
      this.scene.load.image(assetKey, fullPath);

      this.scene.load.once('complete', () => {
        this.loadedAssets.add(assetKey);
        console.log('[UnifiedPlacementManager] Loaded asset:', spriteKey);
        resolve();
      });

      this.scene.load.start();
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
   * 참고: farm_plot은 FarmGridManager에서 별도 처리
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

    // farm_plot 제외하고 렌더링
    items.forEach(item => {
      if (item.itemCode !== 'farm_plot') {
        this.renderItem(item);
      }
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
   * 매 프레임 업데이트
   * 참고: 밭/작물 타이머는 FarmGridManager에서 처리
   */
  update(): void {
    // farm_plot 관련 타이머는 FarmGridManager로 이관됨
    // 이 메서드는 호환성을 위해 유지
  }

  /**
   * 개별 아이템 렌더링
   */
  private renderItem(item: PlacedItem): void {
    const assetKey = this.getAssetKey(item.metadata.sprite);
    const { width, height } = item.metadata;

    // 월드 좌표 계산
    const worldX = item.tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
    const worldY = item.tileY * TILE_SIZE + height * TILE_SIZE;

    const sprite = this.scene.add.sprite(worldX, worldY, assetKey);
    sprite.setOrigin(0.5, 1.0);  // 이미지 하단이 배치 영역 하단에 맞춤

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

    this.placedItems.set(item.id, placedSprite);
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

        // Y좌표 기반 depth 적용
        const depth = getBuildingDepth(finalWorldY, MAP_HEIGHT);
        gameObject.setDepth(depth);

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

    // 맵 범위 체크 (동적 맵 크기 사용)
    if (tileX < 0 || tileX + width > this.mapCols || tileY < 0 || tileY + height > this.mapRows) {
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
   * 특정 타일이 건물/장애물로 막혀있는지 확인 (플레이어 충돌용)
   * @param tileX 타일 X 좌표
   * @param tileY 타일 Y 좌표
   * @returns 막혀있으면 true
   */
  isTileBlocked(tileX: number, tileY: number): boolean {
    // 맵 범위 밖은 막힘 처리 (동적 맵 크기 사용)
    if (tileX < 0 || tileX >= this.mapCols || tileY < 0 || tileY >= this.mapRows) {
      return true;
    }

    // 배치된 아이템과 충돌 체크
    for (const [, placed] of Array.from(this.placedItems.entries())) {
      const { item } = placed;
      const {
        width,
        height,
        collision,
        collisionWidth,
        collisionHeight,
        collisionOffsetX,
        collisionOffsetY
      } = item.metadata;

      // collision이 명시적으로 false면 통과 가능
      if (collision === false) continue;

      // 충돌 영역 계산 (별도 정의가 있으면 사용, 없으면 전체 크기)
      const cWidth = collisionWidth ?? width;
      const cHeight = collisionHeight ?? height;
      const cOffsetX = collisionOffsetX ?? 0;
      const cOffsetY = collisionOffsetY ?? 0;

      // 충돌 영역 시작점
      const collisionStartX = item.tileX + cOffsetX;
      const collisionStartY = item.tileY + cOffsetY;

      // 타일이 충돌 영역 내에 있는지 체크
      if (tileX >= collisionStartX &&
          tileX < collisionStartX + cWidth &&
          tileY >= collisionStartY &&
          tileY < collisionStartY + cHeight) {
        return true;
      }
    }

    return false;
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

    // 동적 맵 크기 사용
    const mapWidth = this.mapCols * TILE_SIZE;
    const mapHeight = this.mapRows * TILE_SIZE;

    // 세로선
    for (let col = 0; col <= this.mapCols; col++) {
      this.gridGraphics.lineBetween(
        col * TILE_SIZE, 0,
        col * TILE_SIZE, mapHeight
      );
    }

    // 가로선
    for (let row = 0; row <= this.mapRows; row++) {
      this.gridGraphics.lineBetween(
        0, row * TILE_SIZE,
        mapWidth, row * TILE_SIZE
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
    // 새로 배치된 아이템이 있는지 확인
    if (this.pendingPlacements.size > 0) {
      return true;
    }

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
    for (const [tempId] of Array.from(this.pendingPlacements.entries())) {
      const placed = this.placedItems.get(tempId);
      if (placed) {
        placed.sprite.destroy();
        this.placedItems.delete(tempId);
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
        const worldX = snapshot.tileX * TILE_SIZE + (width * TILE_SIZE) / 2;
        const worldY = snapshot.tileY * TILE_SIZE + height * TILE_SIZE;
        placed.sprite.setPosition(worldX, worldY);
        const depth = getBuildingDepth(worldY, MAP_HEIGHT);
        placed.sprite.setDepth(depth);
      }
    }

    // 삭제된 아이템 복원
    for (const [id, item] of Array.from(this.deletedItems.entries())) {
      // farm_plot은 복원하지 않음 (FarmGridManager에서 관리)
      if (item.itemCode === 'farm_plot') continue;

      this.renderItem(item);
      // 드래그 모드 상태로 복원
      const placed = this.placedItems.get(id);
      if (placed && placed.item.metadata.canMove) {
        placed.sprite.setInteractive({ draggable: true });
        placed.sprite.setTint(0xaaaaff);
      }
    }

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
      const placed = this.placedItems.get(itemId);

      if (placed) {
        placed.sprite.destroy();
        this.placedItems.delete(itemId);
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
    this.placedItems.delete(itemId);

    return true;
  }

  /**
   * 아이템 로컬 배치 (배치 모드에서만 사용)
   * 실제 API는 호출하지 않고 로컬에서만 렌더링
   * 참고: farm_plot은 FarmGridManager에서 관리하므로 여기서 배치 불가
   * @returns tempId 또는 null (배치 실패 시)
   */
  async placeItemLocally(itemCode: string, tileX: number, tileY: number, metadata: ItemMetadata): Promise<string | null> {
    // farm_plot은 FarmGridManager에서 관리
    if (itemCode === 'farm_plot') {
      return null;
    }

    const { width, height } = metadata;

    // 배치 가능 여부 확인
    if (!this.canPlaceAt(tileX, tileY, width, height)) {
      return null;
    }

    // 에셋 로드 (없으면 로드)
    await this.loadAsset(metadata.sprite);

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
   * 모든 아이템 가져오기
   */
  getPlacedItems(): PlacedItem[] {
    return Array.from(this.placedItems.values()).map(p => p.item);
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
  }

  /**
   * 모든 아이템 정리
   */
  private clearAllItems(): void {
    // 배치된 아이템 정리
    this.placedItems.forEach(placed => {
      placed.sprite.destroy();
    });
    this.placedItems.clear();
  }

  // ====== 충돌 디버그 시각화 ======

  /**
   * 충돌 디버그 토글
   */
  toggleCollisionDebug(): void {
    this.collisionDebugVisible = !this.collisionDebugVisible;
    this.updateCollisionDebug();
  }

  /**
   * 충돌 디버그 표시
   */
  showCollisionDebug(): void {
    this.collisionDebugVisible = true;
    this.updateCollisionDebug();
  }

  /**
   * 충돌 디버그 숨기기
   */
  hideCollisionDebug(): void {
    this.collisionDebugVisible = false;
    this.updateCollisionDebug();
  }

  /**
   * 충돌 영역 시각화 업데이트
   */
  updateCollisionDebug(): void {
    if (!this.collisionDebugGraphics) {
      this.collisionDebugGraphics = this.scene.add.graphics();
      this.collisionDebugGraphics.setDepth(DEPTH.HIGHLIGHT - 2);
    }

    this.collisionDebugGraphics.clear();

    if (!this.collisionDebugVisible) return;

    // 모든 타일에 대해 충돌 체크 (동적 맵 크기 사용)
    for (let tileY = 0; tileY < this.mapRows; tileY++) {
      for (let tileX = 0; tileX < this.mapCols; tileX++) {
        const blocked = this.isTileBlocked(tileX, tileY);

        if (blocked) {
          // 빨간색 반투명으로 충돌 타일 표시
          this.collisionDebugGraphics.fillStyle(0xff0000, 0.3);
          this.collisionDebugGraphics.fillRect(
            tileX * TILE_SIZE,
            tileY * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
          );

          // 테두리
          this.collisionDebugGraphics.lineStyle(1, 0xff0000, 0.6);
          this.collisionDebugGraphics.strokeRect(
            tileX * TILE_SIZE,
            tileY * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
          );
        }
      }
    }

    // 각 배치된 아이템의 충돌 영역 표시 (시안색 테두리)
    for (const [, placed] of Array.from(this.placedItems.entries())) {
      const { item } = placed;
      const {
        width,
        height,
        collision,
        collisionWidth,
        collisionHeight,
        collisionOffsetX,
        collisionOffsetY
      } = item.metadata;

      // collision이 false면 스킵
      if (collision === false) continue;

      // 충돌 영역 계산
      const cWidth = collisionWidth ?? width;
      const cHeight = collisionHeight ?? height;
      const cOffsetX = collisionOffsetX ?? 0;
      const cOffsetY = collisionOffsetY ?? 0;

      const startX = (item.tileX + cOffsetX) * TILE_SIZE;
      const startY = (item.tileY + cOffsetY) * TILE_SIZE;

      // 시안색으로 실제 충돌 영역 테두리
      this.collisionDebugGraphics.lineStyle(2, 0x00ffff, 0.8);
      this.collisionDebugGraphics.strokeRect(
        startX,
        startY,
        cWidth * TILE_SIZE,
        cHeight * TILE_SIZE
      );

      // 전체 배치 영역 (녹색 점선 효과)
      this.collisionDebugGraphics.lineStyle(1, 0x00ff00, 0.4);
      this.collisionDebugGraphics.strokeRect(
        item.tileX * TILE_SIZE,
        item.tileY * TILE_SIZE,
        width * TILE_SIZE,
        height * TILE_SIZE
      );
    }
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

    if (this.collisionDebugGraphics) {
      this.collisionDebugGraphics.destroy();
      this.collisionDebugGraphics = null;
    }
  }
}
