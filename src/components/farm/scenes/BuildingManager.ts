/**
 * BuildingManager - 건물 배치 관리
 * 집, 허수아비, 우물, 닭장 등
 */

import Phaser from 'phaser';
import {
  TILE_SIZE,
  MAP_WIDTH,
  MAP_HEIGHT,
  MAP_COLS,
  MAP_ROWS,
  FARM_OFFSET_X,
  FARM_OFFSET_Y,
} from '../config/gameConfig';
import { DEPTH, getBuildingDepth } from '../config/depthConfig';

// 건물 정의
interface BuildingDef {
  key: string;
  file: string;
  width: number;   // 타일 단위
  height: number;  // 타일 단위
  originY: number; // 스프라이트 originY (바닥 기준)
}

// 건물 에셋 경로
const BUILDING_PATH = '/farm/houses/';

// 건물 정의
const BUILDINGS: Record<string, BuildingDef> = {
  house: {
    key: 'building_house',
    file: 'Farmer_House_1_32x32.png',
    width: 4,
    height: 4,
    originY: 0.9,
  },
  scarecrow: {
    key: 'building_scarecrow',
    file: 'Scarecrow_32x32.png',
    width: 1,
    height: 2,
    originY: 0.9,
  },
  well: {
    key: 'building_well',
    file: 'Well_Usable_Bucket_Full_32x32.png',
    width: 2,
    height: 2,
    originY: 0.85,
  },
  chickenCoop: {
    key: 'building_chicken_coop',
    file: 'Chicken_Coop_32x32.png',
    width: 3,
    height: 3,
    originY: 0.85,
  },
  barn: {
    key: 'building_barn',
    file: 'Barn_Small_32x32.png',
    width: 4,
    height: 3,
    originY: 0.85,
  },
};

// 배치된 건물 정보
interface PlacedBuilding {
  type: string;
  sprite: Phaser.GameObjects.Sprite;
  tileX: number;
  tileY: number;
}

export class BuildingManager {
  private scene: Phaser.Scene;
  private buildings: PlacedBuilding[] = [];

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    Object.values(BUILDINGS).forEach(building => {
      this.scene.load.image(building.key, BUILDING_PATH + building.file);
    });
  }

  /**
   * 기본 건물 배치
   */
  create(): void {
    // 집 - 밭 오른쪽 위
    this.placeBuilding('house', MAP_COLS - 7, 2);

    // 닭장 - 밭 왼쪽
    this.placeBuilding('chickenCoop', 2, FARM_OFFSET_Y);

    // 허수아비 - 밭 왼쪽 위 (밭 근처)
    this.placeBuilding('scarecrow', FARM_OFFSET_X - 3, FARM_OFFSET_Y - 1);

    // 우물 - 집 근처 (오른쪽 아래)
    this.placeBuilding('well', MAP_COLS - 4, 8);
  }

  /**
   * 건물 배치
   * @param type 건물 타입
   * @param tileX 타일 X 좌표
   * @param tileY 타일 Y 좌표
   */
  placeBuilding(type: string, tileX: number, tileY: number): Phaser.GameObjects.Sprite | null {
    const buildingDef = BUILDINGS[type];
    if (!buildingDef) {
      console.warn(`Unknown building type: ${type}`);
      return null;
    }

    // 월드 좌표 계산 (건물 중앙 하단 기준)
    const worldX = tileX * TILE_SIZE + (buildingDef.width * TILE_SIZE) / 2;
    const worldY = tileY * TILE_SIZE + buildingDef.height * TILE_SIZE;

    const sprite = this.scene.add.sprite(worldX, worldY, buildingDef.key);
    sprite.setOrigin(0.5, buildingDef.originY);

    // Y좌표 기반 깊이 설정
    const depth = getBuildingDepth(worldY, MAP_HEIGHT);
    sprite.setDepth(depth);

    this.buildings.push({
      type,
      sprite,
      tileX,
      tileY,
    });

    return sprite;
  }

  /**
   * 건물 제거
   */
  removeBuilding(tileX: number, tileY: number): boolean {
    const index = this.buildings.findIndex(
      b => b.tileX === tileX && b.tileY === tileY
    );

    if (index >= 0) {
      this.buildings[index].sprite.destroy();
      this.buildings.splice(index, 1);
      return true;
    }

    return false;
  }

  /**
   * 특정 위치에 건물이 있는지 확인
   */
  hasBuildingAt(tileX: number, tileY: number): boolean {
    return this.buildings.some(building => {
      const def = BUILDINGS[building.type];
      if (!def) return false;

      return (
        tileX >= building.tileX &&
        tileX < building.tileX + def.width &&
        tileY >= building.tileY &&
        tileY < building.tileY + def.height
      );
    });
  }

  /**
   * 모든 건물 가져오기
   */
  getBuildings(): PlacedBuilding[] {
    return [...this.buildings];
  }

  /**
   * 정리
   */
  destroy(): void {
    this.buildings.forEach(b => b.sprite.destroy());
    this.buildings = [];
  }
}
