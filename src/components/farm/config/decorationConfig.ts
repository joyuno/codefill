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

// 장식 배치 설정
export const DECORATION_CONFIG = {
  // 잔디 개수 (랜덤 배치)
  grassCount: 80,

  // 꽃 개수 (랜덤 배치)
  flowerCount: 40,

  // 나무 배치 (고정 위치) - 집 뒤쪽 제외
  trees: [
    // 왼쪽 위
    { type: 'tree_apple', tileX: 0, tileY: 0 },
    { type: 'tree_pine_small', tileX: 5, tileY: 1 },

    // 왼쪽 아래
    { type: 'tree_pine_medium', tileX: 0, tileY: 14 },
    { type: 'tree_oak_small', tileX: 5, tileY: 15 },

    // 오른쪽 아래
    { type: 'tree_pine_small', tileX: 26, tileY: 14 },
    { type: 'tree_oak_medium', tileX: 24, tileY: 16 },
  ],

  // 건초 배치
  hay: [
    { type: 'hay_pile', tileX: 6, tileY: 10 },
    { type: 'hay_small', tileX: 8, tileY: 11 },
  ],
};
