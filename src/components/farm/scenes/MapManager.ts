/**
 * MapManager - 맵 렌더링 관리
 * 바닥 타일 + 장식 (잔디, 꽃, 나무)
 */

import * as Phaser from 'phaser';
import {
  TILE_SIZE,
  TILESET,
  VIEWPORT_WIDTH,
  VIEWPORT_HEIGHT,
  MAP_COLS,
  FARM_OFFSET_X,
  FARM_OFFSET_Y,
  FARM_MAX_SIZE,
} from '../config/gameConfig';
import { DEPTH } from '../config/depthConfig';

// 잔디 확장 패딩 (화면 전체 커버용)
const GRASS_PADDING = 2000;

export class MapManager {
  private scene: Phaser.Scene;
  private groundTileSprite: Phaser.GameObjects.TileSprite | null = null;
  private decorationSprites: Phaser.GameObjects.Image[] = [];

  // 울타리 스프라이트
  private fenceSprites: Phaser.GameObjects.Image[] = [];

  // 동적 맵 크기
  private mapWidth: number = VIEWPORT_WIDTH;
  private mapHeight: number = VIEWPORT_HEIGHT;

  // 디버그 그리드
  private debugGridGraphics: Phaser.GameObjects.Graphics | null = null;
  private debugGridVisible: boolean = false;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드 (지연 로딩 적용)
   * 필수 에셋만 로드하여 초기 로딩 시간 단축
   * 장식 에셋은 UnifiedPlacementManager에서 필요 시 로드
   */
  preload(): void {
    // 타일셋 (밭 타일용)
    if (!this.scene.textures.exists(TILESET.key)) {
      this.scene.load.spritesheet(TILESET.key, TILESET.path, {
        frameWidth: TILESET.frameWidth,
        frameHeight: TILESET.frameHeight,
      });
    }

    // 바닥 잔디 이미지 (필수)
    if (!this.scene.textures.exists('grass_floor')) {
      this.scene.load.image('grass_floor', '/farm/terrains/grass_floor.png');
    }

    // 울타리 에셋 (4종만 로드, 나머지는 flip으로 처리)
    const fenceAssets = [
      { key: 'fence_border_tl',     path: '/farm/terrains/fence_border_tl.png' },
      { key: 'fence_border_top',    path: '/farm/terrains/fence_border_top.png' },
      { key: 'fence_border_tr',     path: '/farm/terrains/fence_border_tr.png' },
      { key: 'fence_border_left',   path: '/farm/terrains/fence_border_left.png' },
    ];
    for (const asset of fenceAssets) {
      if (!this.scene.textures.exists(asset.key)) {
        this.scene.load.image(asset.key, asset.path);
      }
    }

    console.log('[MapManager] Loading essential assets (2 tiles + 4 fence)');
  }

  /**
   * 맵 생성
   * @param mapWidth 맵 너비 (픽셀)
   * @param mapHeight 맵 높이 (픽셀)
   */
  create(mapWidth?: number, mapHeight?: number): void {
    // 동적 맵 크기 설정
    if (mapWidth) this.mapWidth = mapWidth;
    if (mapHeight) this.mapHeight = mapHeight;

    this.createGrassFloor();
    this.createFenceBorder();
    // 나무와 건초는 소유 시스템으로 전환됨 (PlacementSystem에서 처리)
  }

  /**
   * 잔디 바닥 생성 - TileSprite로 효율적으로 렌더링
   * 맵 크기 + 패딩으로 화면 전체를 커버
   */
  private createGrassFloor(): void {
    const extendedWidth = this.mapWidth + GRASS_PADDING * 2;
    const extendedHeight = this.mapHeight + GRASS_PADDING * 2;

    this.groundTileSprite = this.scene.add.tileSprite(
      this.mapWidth / 2,    // 중앙 x (맵 기준)
      this.mapHeight / 2,   // 중앙 y (맵 기준)
      extendedWidth,        // 확장 너비
      extendedHeight,       // 확장 높이
      'grass_floor'
    );
    this.groundTileSprite.setDepth(DEPTH.GROUND_GRASS);
  }

  /**
   * 잔디 크기 조정 (브라우저 리사이즈 시)
   */
  resizeGrass(viewportWidth: number, viewportHeight: number): void {
    if (!this.groundTileSprite) return;

    const extendedWidth = Math.max(this.mapWidth, viewportWidth) + GRASS_PADDING * 2;
    const extendedHeight = Math.max(this.mapHeight, viewportHeight) + GRASS_PADDING * 2;

    this.groundTileSprite.setSize(extendedWidth, extendedHeight);
  }

  /**
   * 울타리 경계 생성 - 맵 경계 바로 바깥에 나무 울타리 배치
   * 4종 에셋(tl, top, tr, left)만 사용, 나머지는 flip으로 처리
   */
  private createFenceBorder(): void {
    // 기존 울타리 정리
    this.fenceSprites.forEach(s => s.destroy());
    this.fenceSprites = [];

    const cols = Math.floor(this.mapWidth / TILE_SIZE);
    const rows = Math.floor(this.mapHeight / TILE_SIZE);

    // 울타리 depth (잔디 위, 농장 아래)
    const fenceDepth = DEPTH.GROUND_DECORATIONS + 1;  // 3

    const addFence = (x: number, y: number, key: string, flipX = false, flipY = false) => {
      const sprite = this.scene.add.image(x, y, key);
      sprite.setDepth(fenceDepth);
      if (flipX) sprite.setFlipX(true);
      if (flipY) sprite.setFlipY(true);
      this.fenceSprites.push(sprite);
    };

    // 상단 울타리 (원본)
    for (let c = 0; c < cols; c++) {
      addFence(c * TILE_SIZE + TILE_SIZE / 2, -TILE_SIZE / 2, 'fence_border_top');
    }

    // 하단 울타리 (top과 동일 이미지)
    for (let c = 0; c < cols; c++) {
      addFence(c * TILE_SIZE + TILE_SIZE / 2, rows * TILE_SIZE + TILE_SIZE / 2, 'fence_border_top');
    }

    // 좌측 울타리 (원본)
    for (let r = 0; r < rows; r++) {
      addFence(-TILE_SIZE / 2, r * TILE_SIZE + TILE_SIZE / 2, 'fence_border_left');
    }

    // 우측 울타리 (left를 flipX)
    for (let r = 0; r < rows; r++) {
      addFence(cols * TILE_SIZE + TILE_SIZE / 2, r * TILE_SIZE + TILE_SIZE / 2, 'fence_border_left', true);
    }

    // 4개 코너
    addFence(-TILE_SIZE / 2, -TILE_SIZE / 2, 'fence_border_tl');                                           // TL (원본)
    addFence(cols * TILE_SIZE + TILE_SIZE / 2, -TILE_SIZE / 2, 'fence_border_tr');                          // TR (원본)
    addFence(-TILE_SIZE / 2, rows * TILE_SIZE + TILE_SIZE / 2, 'fence_border_tl');                            // BL (tl 동일)
    addFence(cols * TILE_SIZE + TILE_SIZE / 2, rows * TILE_SIZE + TILE_SIZE / 2, 'fence_border_tr');             // BR (tr 동일)

    console.log(`[MapManager] Fence border created: ${cols}x${rows} map, ${this.fenceSprites.length} sprites`);
  }

  /**
   * 금지 구역 체크 (농장, 건물 위치)
   */
  private isRestrictedArea(col: number, row: number): boolean {
    // 농장 영역 (여유 공간 포함)
    const farmPadding = 1;
    if (
      col >= FARM_OFFSET_X - farmPadding &&
      col < FARM_OFFSET_X + FARM_MAX_SIZE + farmPadding &&
      row >= FARM_OFFSET_Y - farmPadding &&
      row < FARM_OFFSET_Y + FARM_MAX_SIZE + farmPadding
    ) {
      return true;
    }

    // 집 영역 (오른쪽 위: MAP_COLS-7, 2)
    if (col >= MAP_COLS - 8 && col <= MAP_COLS - 3 && row >= 1 && row <= 6) {
      return true;
    }

    // 닭장 영역 (왼쪽: 2, FARM_OFFSET_Y)
    if (col >= 1 && col <= 5 && row >= FARM_OFFSET_Y - 1 && row <= FARM_OFFSET_Y + 3) {
      return true;
    }

    // 허수아비 영역
    if (col >= FARM_OFFSET_X - 3 && col <= FARM_OFFSET_X - 1 && row >= FARM_OFFSET_Y - 2 && row <= FARM_OFFSET_Y + 1) {
      return true;
    }

    // 우물 영역 (오른쪽: MAP_COLS-4, 8)
    if (col >= MAP_COLS - 5 && col <= MAP_COLS - 2 && row >= 7 && row <= 10) {
      return true;
    }

    // 나무 영역들 (나무 배치 위치 주변) - 집 뒤쪽 나무 제거됨
    const treeAreas = [
      { x: 0, y: 0, w: 6, h: 6 },    // 왼쪽 위 나무들
      { x: 0, y: 13, w: 7, h: 7 },   // 왼쪽 아래 나무들
      { x: 23, y: 13, w: 7, h: 7 },  // 오른쪽 아래 나무들
    ];

    for (const area of treeAreas) {
      if (col >= area.x && col < area.x + area.w && row >= area.y && row < area.y + area.h) {
        return true;
      }
    }

    return false;
  }

  /**
   * 맵 크기 getter
   */
  getMapDimensions(): { width: number; height: number; cols: number; rows: number } {
    return {
      width: this.mapWidth,
      height: this.mapHeight,
      cols: Math.floor(this.mapWidth / TILE_SIZE),
      rows: Math.floor(this.mapHeight / TILE_SIZE),
    };
  }

  /**
   * 특정 위치가 맵 경계 내인지 확인
   */
  isWithinBounds(x: number, y: number): boolean {
    return x >= 0 && x < this.mapWidth && y >= 0 && y < this.mapHeight;
  }

  /**
   * 월드 좌표를 타일 좌표로 변환
   */
  worldToTile(worldX: number, worldY: number): { col: number; row: number } {
    return {
      col: Math.floor(worldX / TILE_SIZE),
      row: Math.floor(worldY / TILE_SIZE),
    };
  }

  /**
   * 타일 좌표를 월드 좌표(중앙)로 변환
   */
  tileToWorld(col: number, row: number): { x: number; y: number } {
    return {
      x: col * TILE_SIZE + TILE_SIZE / 2,
      y: row * TILE_SIZE + TILE_SIZE / 2,
    };
  }

  /**
   * 디버그 그리드 토글
   */
  toggleDebugGrid(): void {
    this.debugGridVisible = !this.debugGridVisible;
    this.updateDebugGrid();
  }

  /**
   * 디버그 그리드 표시
   */
  showDebugGrid(): void {
    this.debugGridVisible = true;
    this.updateDebugGrid();
  }

  /**
   * 디버그 그리드 숨기기
   */
  hideDebugGrid(): void {
    this.debugGridVisible = false;
    this.updateDebugGrid();
  }

  /**
   * 디버그 그리드 업데이트
   */
  private updateDebugGrid(): void {
    if (!this.debugGridGraphics) {
      this.debugGridGraphics = this.scene.add.graphics();
      this.debugGridGraphics.setDepth(DEPTH.GRID_LINES);
    }

    this.debugGridGraphics.clear();

    if (!this.debugGridVisible) return;

    const mapCols = Math.floor(this.mapWidth / TILE_SIZE);
    const mapRows = Math.floor(this.mapHeight / TILE_SIZE);

    // 노란색 그리드 선
    this.debugGridGraphics.lineStyle(1, 0xffff00, 0.3);

    // 세로선
    for (let col = 0; col <= mapCols; col++) {
      this.debugGridGraphics.lineBetween(
        col * TILE_SIZE, 0,
        col * TILE_SIZE, this.mapHeight
      );
    }

    // 가로선
    for (let row = 0; row <= mapRows; row++) {
      this.debugGridGraphics.lineBetween(
        0, row * TILE_SIZE,
        this.mapWidth, row * TILE_SIZE
      );
    }

    // 타일 좌표 텍스트 (주요 위치만)
    for (let col = 0; col < mapCols; col += 5) {
      for (let row = 0; row < mapRows; row += 5) {
        const x = col * TILE_SIZE + 2;
        const y = row * TILE_SIZE + 2;
        const text = this.scene.add.text(x, y, `${col},${row}`, {
          fontSize: '8px',
          color: '#ffff00',
        });
        text.setDepth(DEPTH.GRID_LINES + 1);
        text.setAlpha(0.5);
        // 나중에 정리를 위해 태그 추가
        text.setData('debugText', true);
      }
    }
  }

  /**
   * 정리
   */
  destroy(): void {
    if (this.groundTileSprite) {
      this.groundTileSprite.destroy();
      this.groundTileSprite = null;
    }
    if (this.debugGridGraphics) {
      this.debugGridGraphics.destroy();
      this.debugGridGraphics = null;
    }
    // 디버그 텍스트 정리
    this.scene.children.list
      .filter(child => child.getData('debugText'))
      .forEach(child => child.destroy());
    this.decorationSprites.forEach(sprite => sprite.destroy());
    this.decorationSprites = [];
    // 울타리 정리
    this.fenceSprites.forEach(sprite => sprite.destroy());
    this.fenceSprites = [];
  }
}
