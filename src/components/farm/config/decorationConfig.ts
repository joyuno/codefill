/**
 * decorationConfig.ts - 장식 요소 설정
 */

import { TILE_SIZE } from './gameConfig';

// 에셋 경로
export const DECORATION_PATH = '/farm/';

// 잔디/꽃 정의 (32x32)
export const GRASS_DECORATIONS = [
  { key: 'grass_1', file: 'terrains/Grass_Tufts_Flowers_32x32_1.png', width: 32, height: 32 },
  { key: 'grass_2', file: 'terrains/Grass_Tufts_Flowers_32x32_2.png', width: 32, height: 32 },
  { key: 'grass_3', file: 'terrains/Grass_Tufts_Flowers_32x32_3.png', width: 32, height: 32 },
  { key: 'grass_4', file: 'terrains/Grass_Tufts_Flowers_32x32_4.png', width: 32, height: 32 },
  { key: 'grass_5', file: 'terrains/Grass_Tufts_Flowers_32x32_5.png', width: 32, height: 32 },
  { key: 'grass_6', file: 'terrains/Grass_Tufts_Flowers_32x32_6.png', width: 32, height: 32 },
  { key: 'grass_7', file: 'terrains/Grass_Tufts_Flowers_32x32_7.png', width: 32, height: 32 },
  { key: 'grass_8', file: 'terrains/Grass_Tufts_Flowers_32x32_8.png', width: 32, height: 32 },
  { key: 'grass_9', file: 'terrains/Grass_Tufts_Flowers_32x32_9.png', width: 32, height: 32 },
  { key: 'grass_10', file: 'terrains/Grass_Tufts_Flowers_32x32_10.png', width: 32, height: 32 },
  { key: 'grass_11', file: 'terrains/Grass_Tufts_Flowers_32x32_11.png', width: 32, height: 32 },
];

// 나무 정의
export const TREE_DECORATIONS = [
  // Oak (참나무) - 크고 둥근 형태
  {
    key: 'tree_oak_small',
    file: 'animated/Trees_Oak_Green_Small_Shake_32x32.gif',
    width: 128,
    height: 128,
    tileWidth: 4,
    tileHeight: 4,
  },
  {
    key: 'tree_oak_medium',
    file: 'animated/Trees_Oak_Green_Medium_Shake_32x32.gif',
    width: 128,
    height: 160,
    tileWidth: 4,
    tileHeight: 5,
  },
  // Pine (소나무) - 뾰족한 형태
  {
    key: 'tree_pine_small',
    file: 'animated/Trees_Pine_Green_Small_Shake_32x32.gif',
    width: 128,
    height: 128,
    tileWidth: 4,
    tileHeight: 4,
  },
  {
    key: 'tree_pine_medium',
    file: 'animated/Trees_Pine_Green_Medium_Shake_32x32.gif',
    width: 128,
    height: 160,
    tileWidth: 4,
    tileHeight: 5,
  },
];

// 과일나무 (작은 크기)
export const FRUIT_TREE_DECORATIONS = [
  {
    key: 'tree_apple',
    file: 'animated/Fruit_Tree_Apple_Ripe_Shake_32x32.gif',
    width: 160,
    height: 160,
    tileWidth: 5,
    tileHeight: 5,
  },
];

// 건초 장식
export const HAY_DECORATIONS = [
  { key: 'hay_pile', file: 'terrains/Hay_Fresh_Pile_32x32.png', width: 64, height: 32 },
  { key: 'hay_small', file: 'terrains/Hay_Fresh_Pile_Small_32x32.png', width: 32, height: 32 },
];

// 꽃 장식 (4가지 색상)
export const FLOWER_DECORATIONS = [
  { key: 'flower_green', file: 'terrains/Flower_Green_32x32.png', width: 32, height: 32 },
  { key: 'flower_pink', file: 'terrains/Flower_Pink_32x32.png', width: 32, height: 32 },
  { key: 'flower_blue', file: 'terrains/Flower_Blue_32x32.png', width: 32, height: 32 },
  { key: 'flower_yellow', file: 'terrains/Flower_Yellow_32x32.png', width: 32, height: 32 },
];

// ==========================================
// 플레이어 배치 가능 아이템 정의
// ==========================================

export interface PlaceableItem {
  key: string;
  name: string;
  category: 'flower' | 'grass';
  assetKey: string;
  file: string;
  width: number;   // 픽셀
  height: number;  // 픽셀
  tileWidth: number;   // 타일 단위
  tileHeight: number;  // 타일 단위
}

// 배치 가능한 꽃
export const PLACEABLE_FLOWERS: PlaceableItem[] = [
  { key: 'flower_blue', name: '파란 꽃', category: 'flower', assetKey: 'flower_blue', file: 'terrains/Flower_Blue_32x32.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'flower_pink', name: '분홍 꽃', category: 'flower', assetKey: 'flower_pink', file: 'terrains/Flower_Pink_32x32.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'flower_yellow', name: '노란 꽃', category: 'flower', assetKey: 'flower_yellow', file: 'terrains/Flower_Yellow_32x32.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'flower_green', name: '초록 꽃', category: 'flower', assetKey: 'flower_green', file: 'terrains/Flower_Green_32x32.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
];

// 배치 가능한 잔디
export const PLACEABLE_GRASS: PlaceableItem[] = [
  { key: 'grass_1', name: '잔디 1', category: 'grass', assetKey: 'grass_1', file: 'terrains/Grass_Tufts_Flowers_32x32_1.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_2', name: '잔디 2', category: 'grass', assetKey: 'grass_2', file: 'terrains/Grass_Tufts_Flowers_32x32_2.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_3', name: '잔디 3', category: 'grass', assetKey: 'grass_3', file: 'terrains/Grass_Tufts_Flowers_32x32_3.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_4', name: '잔디 4', category: 'grass', assetKey: 'grass_4', file: 'terrains/Grass_Tufts_Flowers_32x32_4.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_5', name: '잔디 5', category: 'grass', assetKey: 'grass_5', file: 'terrains/Grass_Tufts_Flowers_32x32_5.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_6', name: '잔디 6', category: 'grass', assetKey: 'grass_6', file: 'terrains/Grass_Tufts_Flowers_32x32_6.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_7', name: '잔디 7', category: 'grass', assetKey: 'grass_7', file: 'terrains/Grass_Tufts_Flowers_32x32_7.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_8', name: '잔디 8', category: 'grass', assetKey: 'grass_8', file: 'terrains/Grass_Tufts_Flowers_32x32_8.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_9', name: '잔디 9', category: 'grass', assetKey: 'grass_9', file: 'terrains/Grass_Tufts_Flowers_32x32_9.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_10', name: '잔디 10', category: 'grass', assetKey: 'grass_10', file: 'terrains/Grass_Tufts_Flowers_32x32_10.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
  { key: 'grass_11', name: '잔디 11', category: 'grass', assetKey: 'grass_11', file: 'terrains/Grass_Tufts_Flowers_32x32_11.png', width: 32, height: 32, tileWidth: 1, tileHeight: 1 },
];

// 전체 배치 가능 아이템
export const PLACEABLE_ITEMS: PlaceableItem[] = [...PLACEABLE_FLOWERS, ...PLACEABLE_GRASS];

// 아이템 키로 PlaceableItem 찾기
export function getPlaceableItem(key: string): PlaceableItem | undefined {
  return PLACEABLE_ITEMS.find(item => item.key === key);
}

// 배치된 장식 데이터 타입
export interface PlacedDecoration {
  id: string;
  itemKey: string;
  tileX: number;
  tileY: number;
}

// ==========================================
// 장식 배치 설정 (바닥 잔디/꽃 - 하드코딩 유지)
// ==========================================
export const DECORATION_CONFIG = {
  // 잔디 개수 (랜덤 배치) - 바닥 장식용
  grassCount: 80,

  // 꽃 개수 (랜덤 배치) - 바닥 장식용
  flowerCount: 40,

  // 나무와 건초는 소유 시스템으로 전환됨 (하드코딩 제거)
};

// ==========================================
// 구매 가능 나무 정의 (상점에서 구매)
// ==========================================
export interface PurchasableTree {
  key: string;
  name: string;
  price: number;
  assetKey: string;
  file: string;
  width: number;
  height: number;
  tileWidth: number;
  tileHeight: number;
}

export const PURCHASABLE_TREES: PurchasableTree[] = [
  {
    key: 'tree_oak_small',
    name: '작은 참나무',
    price: 100,
    assetKey: 'tree_oak_small',
    file: 'animated/Trees_Oak_Green_Small_Shake_32x32.gif',
    width: 128,
    height: 128,
    tileWidth: 4,
    tileHeight: 4,
  },
  {
    key: 'tree_oak_medium',
    name: '중간 참나무',
    price: 200,
    assetKey: 'tree_oak_medium',
    file: 'animated/Trees_Oak_Green_Medium_Shake_32x32.gif',
    width: 128,
    height: 160,
    tileWidth: 4,
    tileHeight: 5,
  },
  {
    key: 'tree_pine_small',
    name: '작은 소나무',
    price: 100,
    assetKey: 'tree_pine_small',
    file: 'animated/Trees_Pine_Green_Small_Shake_32x32.gif',
    width: 128,
    height: 128,
    tileWidth: 4,
    tileHeight: 4,
  },
  {
    key: 'tree_pine_medium',
    name: '중간 소나무',
    price: 200,
    assetKey: 'tree_pine_medium',
    file: 'animated/Trees_Pine_Green_Medium_Shake_32x32.gif',
    width: 128,
    height: 160,
    tileWidth: 4,
    tileHeight: 5,
  },
  {
    key: 'tree_apple',
    name: '사과나무',
    price: 300,
    assetKey: 'tree_apple',
    file: 'animated/Fruit_Tree_Apple_Ripe_Shake_32x32.gif',
    width: 160,
    height: 160,
    tileWidth: 5,
    tileHeight: 5,
  },
];

// ==========================================
// 구매 가능 건초 정의 (상점에서 구매)
// ==========================================
export const PURCHASABLE_HAY: PurchasableTree[] = [
  {
    key: 'hay_pile',
    name: '건초 더미',
    price: 50,
    assetKey: 'hay_pile',
    file: 'terrains/Hay_Fresh_Pile_32x32.png',
    width: 64,
    height: 32,
    tileWidth: 2,
    tileHeight: 1,
  },
  {
    key: 'hay_small',
    name: '작은 건초',
    price: 30,
    assetKey: 'hay_small',
    file: 'terrains/Hay_Fresh_Pile_Small_32x32.png',
    width: 32,
    height: 32,
    tileWidth: 1,
    tileHeight: 1,
  },
];

// 모든 구매 가능 아이템
export const ALL_PURCHASABLE_ITEMS = [...PURCHASABLE_TREES, ...PURCHASABLE_HAY];

// 키로 구매 가능 아이템 찾기
export function getPurchasableTree(key: string): PurchasableTree | undefined {
  return ALL_PURCHASABLE_ITEMS.find(item => item.key === key);
}
