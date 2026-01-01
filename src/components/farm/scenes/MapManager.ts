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
} from '../config/decorationConfig';

export class MapManager {
  private scene: Phaser.Scene;
  private groundTileSprite: Phaser.GameObjects.TileSprite | null = null;
  private decorationSprites: Phaser.GameObjects.Image[] = [];

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    // 타일셋 (밭 타일용)
    this.scene.load.spritesheet(TILESET.key, TILESET.path, {
      frameWidth: TILESET.frameWidth,
      frameHeight: TILESET.frameHeight,
    });

    // 바닥 잔디 이미지
    this.scene.load.image('grass_floor', '/farm/terrains/grass_floor.png');

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
    // 나무와 건초는 소유 시스템으로 전환됨 (PlacementSystem에서 처리)
  }

  /**
   * 잔디 바닥 생성 - TileSprite로 효율적으로 렌더링
   */
  private createGrassFloor(): void {
    // TileSprite: 하나의 이미지를 전체 맵에 반복 (600개 스프라이트 대신 1개)
    this.groundTileSprite = this.scene.add.tileSprite(
      MAP_WIDTH / 2,   // 중앙 x
      MAP_HEIGHT / 2,  // 중앙 y
      MAP_WIDTH,       // 전체 너비
      MAP_HEIGHT,      // 전체 높이
      'grass_floor'
    );
    this.groundTileSprite.setDepth(DEPTH.GROUND_GRASS);
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
    if (this.groundTileSprite) {
      this.groundTileSprite.destroy();
      this.groundTileSprite = null;
    }
    this.decorationSprites.forEach(sprite => sprite.destroy());
    this.decorationSprites = [];
  }
}
