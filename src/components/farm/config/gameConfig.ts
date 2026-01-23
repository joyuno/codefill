/**
 * 게임 설정 상수
 * 스타듀밸리 스타일 농장 게임의 핵심 설정값
 */

// 타일 크기
export const TILE_SIZE = 32;

// 뷰포트 크기 (화면에 보이는 영역 - 고정)
export const VIEWPORT_WIDTH = 960;   // 30 타일
export const VIEWPORT_HEIGHT = 640;  // 20 타일
export const VIEWPORT_COLS = VIEWPORT_WIDTH / TILE_SIZE;   // 30
export const VIEWPORT_ROWS = VIEWPORT_HEIGHT / TILE_SIZE;  // 20

// 맵 확장 단계 (중심에서 사방으로 확장)
export const MAP_EXPANSION_STAGES = {
  1: { cols: 30, rows: 20, name: '작은 땅', cost: 0 },
  2: { cols: 45, rows: 30, name: '넓은 땅', cost: 5000 },
  3: { cols: 60, rows: 40, name: '큰 땅', cost: 15000 },
  4: { cols: 80, rows: 50, name: '대농장', cost: 35000 },
  5: { cols: 100, rows: 60, name: '거대 농장', cost: 70000 },
} as const;

export const MAP_EXPANSION_ORDER = [1, 2, 3, 4, 5] as const;

// 기본 맵 크기 (1단계 기준, 동적으로 변경됨)
export const DEFAULT_MAP_LEVEL = 1;
export const MAP_WIDTH = MAP_EXPANSION_STAGES[DEFAULT_MAP_LEVEL].cols * TILE_SIZE;   // 960
export const MAP_HEIGHT = MAP_EXPANSION_STAGES[DEFAULT_MAP_LEVEL].rows * TILE_SIZE;  // 640

// 맵 크기 헬퍼 함수
export function getMapDimensions(level: number) {
  const stage = MAP_EXPANSION_STAGES[level as keyof typeof MAP_EXPANSION_STAGES]
    || MAP_EXPANSION_STAGES[1];
  return {
    cols: stage.cols,
    rows: stage.rows,
    width: stage.cols * TILE_SIZE,
    height: stage.rows * TILE_SIZE,
    name: stage.name,
    cost: stage.cost,
  };
}

export const MAP_COLS = MAP_WIDTH / TILE_SIZE;   // 30
export const MAP_ROWS = MAP_HEIGHT / TILE_SIZE;  // 20

// 농장 영역 설정 (맵 중앙)
export const FARM_MAX_SIZE = 7;    // 최대 7x7
export const FARM_START_SIZE = 3;  // 초기 3x3

// 농장 위치 계산 (맵 중앙)
export const FARM_OFFSET_X = Math.floor((MAP_COLS - FARM_MAX_SIZE) / 2);  // 12
export const FARM_OFFSET_Y = Math.floor((MAP_ROWS - FARM_MAX_SIZE) / 2);  // 7

// 플레이어 설정
export const PLAYER_SPEED = 150;
export const PLAYER_START_X = MAP_WIDTH / 2;
export const PLAYER_START_Y = MAP_HEIGHT / 2 + TILE_SIZE * 2;  // 농장 아래쪽

// 상호작용 설정
export const INTERACTION_RADIUS = 48;  // 1.5 타일

// 애니메이션 프레임 설정
export const ANIMATION_FRAME_RATE = 8;
export const HARVEST_FRAME_RATE = 12;
export const WATER_FRAME_RATE = 10;

// 카메라 설정
export const CAMERA_LERP = 0.1;  // 부드러운 카메라 추적

// 타일셋 정보
export const TILESET = {
  key: 'terrain_sheet',
  path: '/farm/terrains/1_Terrains_32x32.png',
  frameWidth: TILE_SIZE,
  frameHeight: TILE_SIZE,
  columns: 32,
  rows: 23,
};

// 타일 인덱스 (1_Terrains_32x32.png 기준)
export const TILES = {
  // 잔디 - 11행 4열 (1-indexed) = (10 * 32) + 3 = 323
  GRASS_GREEN: 323,         // 초록색 잔디 (통일용)
  GRASS_PURE: 75,           // 순수 잔디 (기존)
  GRASS_FLOWER_1: 76,       // 꽃 있는 잔디 1
  GRASS_FLOWER_2: 77,       // 꽃 있는 잔디 2
  DIRT_CENTER: 40,          // 흙 중앙
  DIRT_TOP_LEFT: 7,         // 흙 모서리들
  DIRT_TOP: 8,
  DIRT_TOP_RIGHT: 9,
  DIRT_LEFT: 39,
  DIRT_RIGHT: 41,
  DIRT_BOTTOM_LEFT: 71,
  DIRT_BOTTOM: 72,
  DIRT_BOTTOM_RIGHT: 73,
};

// 밭 전용 스프라이트시트 (farm_plot.png - 3x3, 각 32x32)
export const FARM_TILESET = {
  key: 'farm_plot_tiles',
  path: '/farm/terrains/farm_plot.png',
  frameWidth: TILE_SIZE,
  frameHeight: TILE_SIZE,
  columns: 3,
  rows: 3,
};

// 밭 타일 (9-patch 방식) - farm_plot.png 프레임 번호
export const FARM_TILES = {
  TOP_LEFT: 0,      // 1행 1열: 좌상단 모서리
  TOP: 1,           // 1행 2열: 상단
  TOP_RIGHT: 2,     // 1행 3열: 우상단 모서리
  LEFT: 3,          // 2행 1열: 좌측
  CENTER: 4,        // 2행 2열: 중앙 (심을 수 있는 칸)
  RIGHT: 5,         // 2행 3열: 우측
  BOTTOM_LEFT: 6,   // 3행 1열: 좌하단 모서리
  BOTTOM: 7,        // 3행 2열: 하단
  BOTTOM_RIGHT: 8,  // 3행 3열: 우하단 모서리
};

// 격자선 설정
export const GRID = {
  color: 0x000000,
  alpha: 0.08,
  lineWidth: 1,
};

// 농장 슬롯 상태
export const SLOT_STATE = {
  EMPTY: 'empty',
  PLANTED: 'planted',
  READY: 'ready',
} as const;

// 작물 성장 단계
export const GROWTH_STAGES = {
  SEED: 0,
  SPROUT: 1,
  GROWING: 2,
  MATURE: 3,
  HARVEST: 4,
} as const;

export type SlotState = typeof SLOT_STATE[keyof typeof SLOT_STATE];
export type GrowthStage = typeof GROWTH_STAGES[keyof typeof GROWTH_STAGES];
