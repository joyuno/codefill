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
  stageFrames: number[];           // 각 성장 단계별 프레임 인덱스
  harvestFrame: number;            // 수확 가능 프레임
  frameWidth: number;              // 프레임 너비
  frameHeight: number;             // 프레임 높이
  offsetY: number;                 // Y축 오프셋 (큰 작물용)
}

// Growth Stages 스프라이트시트는 보통 5프레임:
// [0] 씨앗/새싹, [1] 성장1, [2] 성장2, [3] 성장3, [4] 수확 가능
const DEFAULT_STAGE_FRAMES = [0, 1, 2, 3, 4];

export const CROPS: Record<string, CropConfig> = {
  carrot: {
    code: 'carrot',
    name: 'Carrot',
    nameKo: '당근',
    spritesheet: 'Carrot_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Carrot_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  tomato: {
    code: 'tomato',
    name: 'Tomato',
    nameKo: '토마토',
    spritesheet: 'Tomato_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Tomato_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  corn: {
    code: 'corn',
    name: 'Corn',
    nameKo: '옥수수',
    spritesheet: 'Corn_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Corn_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE * 2,  // 옥수수는 키가 큼
    offsetY: -TILE_SIZE / 2,
  },
  strawberry: {
    code: 'strawberry',
    name: 'Strawberry',
    nameKo: '딸기',
    spritesheet: 'Strawberry_Growth_Stages_32x32.png',
    seedSprite: 'Seed_strawberry_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  pumpkin: {
    code: 'pumpkin',
    name: 'Pumpkin',
    nameKo: '호박',
    spritesheet: 'Pumpkin_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Pumpkin_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  cabbage: {
    code: 'cabbage',
    name: 'Cabbage',
    nameKo: '양배추',
    spritesheet: 'Cabbage_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Cabbage_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  radish: {
    code: 'radish',
    name: 'Radish',
    nameKo: '무',
    spritesheet: 'Radish_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Radish_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  onion: {
    code: 'onion',
    name: 'Onion',
    nameKo: '양파',
    spritesheet: 'Onion_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Onion_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  potato: {
    code: 'potato',
    name: 'Potato',
    nameKo: '감자',
    // 감자 스프라이트가 없어서 Turnip(순무)으로 대체 (비슷한 뿌리채소)
    spritesheet: 'Turnip_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Turnip_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
  },
  wheat: {
    code: 'wheat',
    name: 'Wheat',
    nameKo: '밀',
    spritesheet: 'Wheat_Growth_Stages_32x32.png',
    seedSprite: 'Seed_Grain_32x32.png',
    stageFrames: DEFAULT_STAGE_FRAMES,
    harvestFrame: 4,
    frameWidth: TILE_SIZE,
    frameHeight: TILE_SIZE,
    offsetY: 0,
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
