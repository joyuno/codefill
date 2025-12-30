/**
 * Depth 레이어 설정
 * Phaser에서 렌더링 순서를 관리하기 위한 깊이값
 *
 * 숫자가 클수록 위에 렌더링됨
 */

// 기본 레이어 깊이
export const DEPTH = {
  // 바닥 레이어 (0-9)
  GROUND_GRASS: 0,
  GROUND_DECORATIONS: 2,
  GRID_LINES: 5,

  // 농장 레이어 (10-99)
  FARM_BACKGROUND: 10,      // 밭 배경
  SOIL_TILES: 15,           // 흙 타일
  CROP_BASE: 20,            // 작물 기준값 (y좌표에 따라 20-80)

  // 엔티티 레이어 (100-199)
  ENTITY_BASE: 100,         // 캐릭터/동물 기준값 (y좌표에 따라 100-180)
  ENTITY_MAX: 180,

  // 건물 레이어 (200-299)
  BUILDING_BASE: 200,
  BUILDING_SHADOW: 195,
  BUILDING_MAX: 250,

  // UI 레이어 (500+)
  HIGHLIGHT: 500,
  INDICATOR: 510,
  TOOLTIP: 520,
  OVERLAY: 600,
} as const;

/**
 * Y좌표 기반 깊이 계산 (엔티티용)
 * 아래에 있는 객체가 위에 있는 객체 앞에 렌더링됨
 *
 * @param y - 월드 좌표 Y값
 * @param mapHeight - 맵 높이 (픽셀)
 * @returns 계산된 깊이값 (100-180 범위)
 */
export function getEntityDepth(y: number, mapHeight: number): number {
  const normalizedY = Math.max(0, Math.min(y / mapHeight, 1));
  return DEPTH.ENTITY_BASE + Math.floor(normalizedY * (DEPTH.ENTITY_MAX - DEPTH.ENTITY_BASE));
}

/**
 * Y좌표 기반 깊이 계산 (작물용)
 *
 * @param y - 월드 좌표 Y값
 * @param mapHeight - 맵 높이 (픽셀)
 * @returns 계산된 깊이값 (20-80 범위)
 */
export function getCropDepth(y: number, mapHeight: number): number {
  const normalizedY = Math.max(0, Math.min(y / mapHeight, 1));
  return DEPTH.CROP_BASE + Math.floor(normalizedY * 60);  // 20 + (0-60)
}

/**
 * 건물 깊이 계산
 * 건물 바닥 Y좌표 기준
 *
 * @param bottomY - 건물 바닥 Y좌표
 * @param mapHeight - 맵 높이
 * @returns 계산된 깊이값
 */
export function getBuildingDepth(bottomY: number, mapHeight: number): number {
  const normalizedY = Math.max(0, Math.min(bottomY / mapHeight, 1));
  return DEPTH.BUILDING_BASE + Math.floor(normalizedY * 50);  // 200 + (0-50)
}

export type DepthLayer = typeof DEPTH[keyof typeof DEPTH];
