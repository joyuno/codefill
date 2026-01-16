/**
 * 작물 설정
 * 작물 코드와 스프라이트 매핑
 */

import { TILE_SIZE } from './gameConfig';

// 작물별 스프라이트 설정
export interface CropConfig {
  code: string;                    // DB 작물 코드
  name: string;                    // 영문 이름
  nameKo: string;                  // 한글 이름
  spritesheet: string;             // Growth Stages 스프라이트시트 파일명
  seedSprite: string;              // 씨앗 스프라이트 파일명
  ripeSprite: string;              // 성숙한 작물 스프라이트 파일명
  stageFrames: number[];           // 각 성장 단계별 프레임 인덱스
  harvestFrame: number;            // 수확 가능 프레임
  frameWidth: number;              // 프레임 너비
  frameHeight: number;             // 프레임 높이
  offsetY: number;                 // Y축 오프셋 (큰 작물용)
}

// Growth Stages 스프라이트시트는 7프레임:
// [0] 씨앗, [1] 새싹, [2] 성장1, [3] 성장2, [4] 성장3, [5] 성장4, [6] 수확 가능
const DEFAULT_STAGE_FRAMES = [0, 1, 2, 3, 4, 5, 6];

export const CROPS: Record<string, CropConfig> = {
  // ==================== Common (6) ====================
  carrot: {
    code: 'carrot',
    name: 'Carrot',
    nameKo: '당근',
    spritesheet: '/farm/icons/crops/Carrot/growth.png',
    seedSprite: 'Seed_Carrot_32x32.png',
    ripeSprite: '/farm/icons/crops/Carrot/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  radish: {
    code: 'radish',
    name: 'Radish',
    nameKo: '무',
    spritesheet: '/farm/icons/crops/Radish/growth.png',
    seedSprite: 'Seed_Radish_32x32.png',
    ripeSprite: '/farm/icons/crops/Radish/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  turnip: {
    code: 'turnip',
    name: 'Turnip',
    nameKo: '순무',
    spritesheet: '/farm/icons/crops/Turnip/growth.png',
    seedSprite: 'Seed_Turnip_32x32.png',
    ripeSprite: '/farm/icons/crops/Turnip/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  onion: {
    code: 'onion',
    name: 'Onion',
    nameKo: '양파',
    spritesheet: '/farm/icons/crops/Onion/growth.png',
    seedSprite: 'Seed_Onion_32x32.png',
    ripeSprite: '/farm/icons/crops/Onion/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  tomato: {
    code: 'tomato',
    name: 'Tomato',
    nameKo: '토마토',
    spritesheet: '/farm/icons/crops/Tomato/growth.png',
    seedSprite: 'Seed_Tomato_32x32.png',
    ripeSprite: '/farm/icons/crops/Tomato/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  grain: {
    code: 'grain',
    name: 'Grain',
    nameKo: '곡물',
    spritesheet: '/farm/icons/crops/Grain/growth.png',
    seedSprite: 'Seed_Grain_32x32.png',
    ripeSprite: '/farm/icons/crops/Grain/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },

  // ==================== Uncommon (6) ====================
  cauliflower: {
    code: 'cauliflower',
    name: 'Cauliflower',
    nameKo: '콜리플라워',
    spritesheet: '/farm/icons/crops/Cauliflower/growth.png',
    seedSprite: 'Seed_Cauliflower_32x32.png',
    ripeSprite: '/farm/icons/crops/Cauliflower/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  corn: {
    code: 'corn',
    name: 'Corn',
    nameKo: '옥수수',
    spritesheet: '/farm/icons/crops/Corn/growth.png',
    seedSprite: 'Seed_Corn_32x32.png',
    ripeSprite: '/farm/icons/crops/Corn/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  chili_pepper: {
    code: 'chili_pepper',
    name: 'Chili Pepper',
    nameKo: '고추',
    spritesheet: '/farm/icons/crops/Chili_Pepper/growth.png',
    seedSprite: 'Seed_Chili_Pepper_32x32.png',
    ripeSprite: '/farm/icons/crops/Chili_Pepper/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  strawberry: {
    code: 'strawberry',
    name: 'Strawberry',
    nameKo: '딸기',
    spritesheet: '/farm/icons/crops/Strawberry/growth.png',
    seedSprite: 'Seed_strawberry_32x32.png',
    ripeSprite: '/farm/icons/crops/Strawberry/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  zucchini: {
    code: 'zucchini',
    name: 'Zucchini',
    nameKo: '주키니',
    spritesheet: '/farm/icons/crops/Zucchini/growth.png',
    seedSprite: 'Seed_Zucchini_32x32.png',
    ripeSprite: '/farm/icons/crops/Zucchini/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  cotton: {
    code: 'cotton',
    name: 'Cotton',
    nameKo: '목화',
    spritesheet: '/farm/icons/crops/Cotton/growth.png',
    seedSprite: 'Seed_Cotton_32x32.png',
    ripeSprite: '/farm/icons/crops/Cotton/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },

  // ==================== Rare (4) ====================
  pumpkin: {
    code: 'pumpkin',
    name: 'Pumpkin',
    nameKo: '호박',
    spritesheet: '/farm/icons/crops/Pumpkin/growth.png',
    seedSprite: 'Seed_Pumpkin_32x32.png',
    ripeSprite: '/farm/icons/crops/Pumpkin/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  grape: {
    code: 'grape',
    name: 'Grape',
    nameKo: '포도',
    spritesheet: '/farm/icons/crops/Grape/growth.png',
    seedSprite: 'Seed_Grapes_32x32.png',
    ripeSprite: '/farm/icons/crops/Grape/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  coffee: {
    code: 'coffee',
    name: 'Coffee',
    nameKo: '커피',
    spritesheet: '/farm/icons/crops/Coffee/growth.png',
    seedSprite: 'Seed_Berry_32x32.png',
    ripeSprite: '/farm/icons/crops/Coffee/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  prickly_pear: {
    code: 'prickly_pear',
    name: 'Prickly Pear',
    nameKo: '백년초',
    spritesheet: '/farm/icons/crops/Prickly_Pear/growth.png',
    seedSprite: 'Seed_Prickly_Pear_32x32.png',
    ripeSprite: '/farm/icons/crops/Prickly_Pear/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 3,
    offsetY: -TILE_SIZE,
  },

  // ==================== Epic (2) ====================
  watermelon: {
    code: 'watermelon',
    name: 'Watermelon',
    nameKo: '수박',
    spritesheet: '/farm/icons/crops/Watermelon/growth.png',
    seedSprite: 'Seed_Watermelon_32x32.png',
    ripeSprite: '/farm/icons/crops/Watermelon/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
  pineapple: {
    code: 'pineapple',
    name: 'Pineapple',
    nameKo: '파인애플',
    spritesheet: '/farm/icons/crops/Pineapple/growth.png',
    seedSprite: 'Seed_Pineapple_32x32.png',
    ripeSprite: '/farm/icons/crops/Pineapple/icon.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 6,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,
    offsetY: -TILE_SIZE / 2,
  },
};

// 에셋 경로
export const CROP_ASSET_PATH = '/farm/crops/';

/**
 * 작물 코드로 설정 가져오기
 */
export function getCropConfig(cropCode: string): CropConfig | null {
  return CROPS[cropCode] || null;
}

/**
 * 성장 단계에 해당하는 프레임 인덱스 가져오기
 */
export function getCropFrame(cropCode: string, stage: number): number {
  const config = getCropConfig(cropCode);
  if (!config) return 0;

  const clampedStage = Math.max(0, Math.min(stage, config.stageFrames.length - 1));
  return config.stageFrames[clampedStage];
}

/**
 * 작물이 수확 가능한지 확인
 */
export function isHarvestReady(cropCode: string, stage: number): boolean {
  const config = getCropConfig(cropCode);
  if (!config) return false;

  return stage >= config.stageFrames.length - 1;
}

/**
 * 모든 작물 코드 목록
 */
export function getAllCropCodes(): string[] {
  return Object.keys(CROPS);
}

/**
 * 작물 스프라이트시트 로드 키 생성
 */
export function getCropSpriteKey(cropCode: string): string {
  return `crop_${cropCode}`;
}

/**
 * 씨앗 스프라이트 로드 키 생성
 */
export function getSeedSpriteKey(cropCode: string): string {
  return `seed_${cropCode}`;
}
