/**
 * MapManager - 맵 렌더링 관리
 * 바닥 타일 + 장식 (잔디, 꽃, 나무)
 */

import Phaser from 'phaser';
import {
  MAP_COLS,
  MAP_ROWS,
  MAP_WIDTH,
  MAP_HEIGHT,
  TILE_SIZE,
  TILESET,
  TILES,
  FARM_OFFSET_X,
  FARM_OFFSET_Y,
  FARM_MAX_SIZE,
} from '../config/gameConfig';
import { DEPTH, getBuildingDepth } from '../config/depthConfig';
import {
  DECORATION_PATH,
  GRASS_DECORATIONS,
  TREE_DECORATIONS,
  FRUIT_TREE_DECORATIONS,
  HAY_DECORATIONS,
  FLOWER_DECORATIONS,
  DECORATION_CONFIG,
} from '../config/decorationConfig';

export class MapManager {
  private scene: Phaser.Scene;
  private groundSprites: Phaser.GameObjects.Sprite[] = [];
  private decorationSprites: Phaser.GameObjects.Image[] = [];

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    // 타일셋
    this.scene.load.spritesheet(TILESET.key, TILESET.path, {
      frameWidth: TILESET.frameWidth,
      frameHeight: TILESET.frameHeight,
    });

    // 잔디/꽃
    GRASS_DECORATIONS.forEach(grass => {
      this.scene.load.image(grass.key, DECORATION_PATH + grass.file);
    });

    // 나무
    TREE_DECORATIONS.forEach(tree => {
      this.scene.load.image(tree.key, DECORATION_PATH + tree.file);
    });

    // 과일나무
    FRUIT_TREE_DECORATIONS.forEach(tree => {
      this.scene.load.image(tree.key, DECORATION_PATH + tree.file);
    });

    // 건초
    HAY_DECORATIONS.forEach(hay => {
      this.scene.load.image(hay.key, DECORATION_PATH + hay.file);
    });

    // 꽃 (개별 이미지)
    FLOWER_DECORATIONS.forEach(flower => {
      this.scene.load.image(flower.key, DECORATION_PATH + flower.file);
    });
  }

  /**
   * 맵 생성
   */
  create(): void {
    this.createGrassFloor();
    this.createGrassDecorations();
    this.createFlowerDecorations();
    this.createTrees();
    this.createHayDecorations();
  }

  /**
   * 잔디 바닥 생성 - 전체 맵을 초록색 잔디로 통일
   */
  private createGrassFloor(): void {
    for (let row = 0; row < MAP_ROWS; row++) {
      for (let col = 0; col < MAP_COLS; col++) {
        const x = col * TILE_SIZE + TILE_SIZE / 2;
        const y = row * TILE_SIZE + TILE_SIZE / 2;

        const tile = this.scene.add.sprite(x, y, TILESET.key, TILES.GRASS_GREEN);
        tile.setDepth(DEPTH.GROUND_GRASS);
        this.groundSprites.push(tile);
      }
    }
  }

  /**
   * 잔디/꽃 장식 생성 - 랜덤 배치
   */
  private createGrassDecorations(): void {
    const count = DECORATION_CONFIG.grassCount;
    let placed = 0;
    let attempts = 0;
    const maxAttempts = count * 10;

    while (placed < count && attempts < maxAttempts) {
      attempts++;

      // 랜덤 위치
      const col = Math.floor(Math.random() * MAP_COLS);
      const row = Math.floor(Math.random() * MAP_ROWS);

      // 금지 구역 체크
      if (this.isRestrictedArea(col, row)) continue;

      // 랜덤 잔디 선택
      const grassIndex = Math.floor(Math.random() * GRASS_DECORATIONS.length);
      const grass = GRASS_DECORATIONS[grassIndex];

      // 약간의 오프셋 추가 (자연스러움)
      const offsetX = (Math.random() - 0.5) * 16;
      const offsetY = (Math.random() - 0.5) * 16;

      const x = col * TILE_SIZE + TILE_SIZE / 2 + offsetX;
      const y = row * TILE_SIZE + TILE_SIZE / 2 + offsetY;

      const sprite = this.scene.add.image(x, y, grass.key);
      sprite.setDepth(DEPTH.GROUND_DECORATIONS);

      // 투명도 높여서 잘 보이게 (0.85~1.0)
      sprite.setAlpha(0.85 + Math.random() * 0.15);

      this.decorationSprites.push(sprite);
      placed++;
    }
  }

  /**
   * 꽃 장식 생성 - 4가지 색상 꽃 랜덤 배치
   */
  private createFlowerDecorations(): void {
    const count = DECORATION_CONFIG.flowerCount;
    let placed = 0;
    let attempts = 0;
    const maxAttempts = count * 10;

    while (placed < count && attempts < maxAttempts) {
      attempts++;

      // 랜덤 위치
      const col = Math.floor(Math.random() * MAP_COLS);
      const row = Math.floor(Math.random() * MAP_ROWS);

      // 금지 구역 체크
      if (this.isRestrictedArea(col, row)) continue;

      // 랜덤 꽃 선택
      const flowerDef = FLOWER_DECORATIONS[Math.floor(Math.random() * FLOWER_DECORATIONS.length)];

      // 약간의 오프셋 추가 (자연스러움)
      const offsetX = (Math.random() - 0.5) * 16;
      const offsetY = (Math.random() - 0.5) * 16;

      const x = col * TILE_SIZE + TILE_SIZE / 2 + offsetX;
      const y = row * TILE_SIZE + TILE_SIZE / 2 + offsetY;

      const sprite = this.scene.add.image(x, y, flowerDef.key);
      sprite.setDepth(DEPTH.GROUND_DECORATIONS + 1);

      this.decorationSprites.push(sprite);
      placed++;
    }
  }

  /**
   * 나무 배치
   */
  private createTrees(): void {
    DECORATION_CONFIG.trees.forEach(treePlacement => {
      const treeDef = [...TREE_DECORATIONS, ...FRUIT_TREE_DECORATIONS]
        .find(t => t.key === treePlacement.type);

      if (!treeDef) return;

      // 나무 중앙 하단 기준 위치
      const x = treePlacement.tileX * TILE_SIZE + treeDef.width / 2;
      const y = treePlacement.tileY * TILE_SIZE + treeDef.height;

      const sprite = this.scene.add.image(x, y, treeDef.key);
      sprite.setOrigin(0.5, 1); // 하단 중앙

      // Y좌표 기반 깊이 (건물과 같은 방식)
      const depth = getBuildingDepth(y, MAP_HEIGHT);
      sprite.setDepth(depth);

      this.decorationSprites.push(sprite);
    });
  }

  /**
   * 건초 장식 배치
   */
  private createHayDecorations(): void {
    DECORATION_CONFIG.hay.forEach(hayPlacement => {
      const hayDef = HAY_DECORATIONS.find(h => h.key === hayPlacement.type);
      if (!hayDef) return;

      const x = hayPlacement.tileX * TILE_SIZE + hayDef.width / 2;
      const y = hayPlacement.tileY * TILE_SIZE + hayDef.height;

      const sprite = this.scene.add.image(x, y, hayDef.key);
      sprite.setOrigin(0.5, 1);
      sprite.setDepth(DEPTH.GROUND_DECORATIONS + 1);

      this.decorationSprites.push(sprite);
    });
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
   * 특정 위치가 맵 경계 내인지 확인
   */
  isWithinBounds(x: number, y: number): boolean {
    return x >= 0 && x < MAP_WIDTH && y >= 0 && y < MAP_HEIGHT;
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
   * 정리
   */
  destroy(): void {
    this.groundSprites.forEach(sprite => sprite.destroy());
    this.groundSprites = [];
    this.decorationSprites.forEach(sprite => sprite.destroy());
    this.decorationSprites = [];
  }
}
