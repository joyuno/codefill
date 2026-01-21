/**
 * InteractionSystem - 상호작용 시스템
 * 슬롯 하이라이트, 액션 인디케이터, 근처 밭 슬롯 감지
 *
 * 리팩토링: farm_plot → slot 기반 시스템
 */

import * as Phaser from 'phaser';
import { TILE_SIZE } from '../config/gameConfig';
import { DEPTH } from '../config/depthConfig';
import { PlayerController } from './PlayerController';
import type { FarmGridManager, FarmSlot } from './FarmGridManager';

// 상호작용 타입
export type InteractionType = 'plant' | 'harvest' | 'none';

// 슬롯 상호작용 정보
export interface SlotInteraction {
  slot: number;
  slotData: FarmSlot;
  centerX: number;
  centerY: number;
}

// React로 상호작용 상태 전달을 위한 콜백 타입
export type InteractionCallback = (interaction: {
  type: InteractionType;
  cropCode: string | null;
  stage: number;
} | null) => void;

export class InteractionSystem {
  private scene: Phaser.Scene;
  private playerController: PlayerController;
  private farmGridManager: FarmGridManager | null = null;

  private highlightGraphics: Phaser.GameObjects.Graphics;

  private currentSlot: SlotInteraction | null = null;
  private currentInteraction: InteractionType = 'none';

  // 현재 farm_slots 데이터 (FarmScene에서 업데이트)
  private farmSlots: FarmSlot[] = [];

  // React 콜백 (상호작용 상태 변경 시 호출)
  private onInteractionChange: InteractionCallback | null = null;

  // 코너 마커 애니메이션용
  private cornerAlpha: number = 0.8;
  private cornerAlphaDirection: number = -1;

  constructor(
    scene: Phaser.Scene,
    playerController: PlayerController
  ) {
    this.scene = scene;
    this.playerController = playerController;

    // 하이라이트 그래픽스 (흙 위, 작물/캐릭터 아래)
    this.highlightGraphics = scene.add.graphics();
    this.highlightGraphics.setDepth(DEPTH.SOIL_TILES + 3);  // 15 + 3 = 18 (작물 20 아래)
  }

  /**
   * React 콜백 설정
   */
  setInteractionCallback(callback: InteractionCallback): void {
    this.onInteractionChange = callback;
  }

  /**
   * FarmGridManager 설정
   */
  setFarmGridManager(manager: FarmGridManager): void {
    this.farmGridManager = manager;
  }

  /**
   * farm_slots 데이터 업데이트
   */
  updateFarmSlots(slots: FarmSlot[]): void {
    this.farmSlots = slots;
  }

  /**
   * 매 프레임 업데이트
   * @param selectedSeed 현재 선택된 씨앗 코드
   */
  update(selectedSeed: string | null): void {
    if (!this.farmGridManager) return;

    const playerPos = this.playerController.getPosition();
    const nearestSlot = this.findNearestSlot(playerPos.x, playerPos.y);

    // 슬롯 변경 감지
    const slotChanged = nearestSlot?.slot !== this.currentSlot?.slot;
    if (slotChanged) {
      this.currentSlot = nearestSlot;
    }

    // 상호작용 타입 결정
    const prevInteraction = this.currentInteraction;
    if (nearestSlot) {
      this.currentInteraction = this.determineInteraction(nearestSlot.slotData, selectedSeed);
    } else {
      this.currentInteraction = 'none';
    }

    // 하이라이트 업데이트 (매 프레임 - 애니메이션용)
    this.updateHighlight();

    // React에 상호작용 상태 전달 (변경 시에만)
    if (slotChanged || prevInteraction !== this.currentInteraction) {
      this.notifyInteractionChange();
    }
  }

  /**
   * React에 상호작용 상태 변경 알림
   */
  private notifyInteractionChange(): void {
    if (!this.onInteractionChange) return;

    if (this.currentInteraction === 'none' || !this.currentSlot) {
      this.onInteractionChange(null);
    } else {
      this.onInteractionChange({
        type: this.currentInteraction,
        cropCode: this.currentSlot.slotData.cropCode,
        stage: this.currentSlot.slotData.stage,
      });
    }
  }

  /**
   * 플레이어 중앙이 밭 슬롯 위에 있는지 확인
   * (타일 영역 판정)
   */
  private findNearestSlot(playerX: number, playerY: number): SlotInteraction | null {
    if (!this.farmGridManager) return null;

    // 플레이어 판정 위치 (발에서 10px 위)
    const centerY = playerY - 10;
    const slotIndex = this.farmGridManager.getSlotAt(playerX, centerY);

    // 밭 위에 없으면 null
    if (slotIndex === null) return null;

    // 슬롯 중심 좌표 가져오기
    const center = this.farmGridManager.getSlotCenter(slotIndex);
    if (!center) return null;

    // 슬롯 데이터 조회
    const slotData = this.farmSlots.find(s => s.slot === slotIndex) || {
      slot: slotIndex,
      cropCode: null,
      plantedAt: null,
      growTimeSeconds: null,
      stage: 0,
    };

    return {
      slot: slotIndex,
      slotData,
      centerX: center.x,
      centerY: center.y,
    };
  }

  /**
   * 상호작용 타입 결정
   */
  private determineInteraction(
    slotData: FarmSlot,
    selectedSeed: string | null
  ): InteractionType {
    // 작물이 있고 수확 가능한 경우 (stage >= 6)
    if (slotData.cropCode && slotData.stage >= 6) {
      return 'harvest';
    }

    // 빈 슬롯이고 씨앗이 선택된 경우
    if (!slotData.cropCode && selectedSeed) {
      return 'plant';
    }

    return 'none';
  }

  /**
   * 하이라이트 업데이트 - 코너 마커 스타일
   */
  private updateHighlight(): void {
    this.highlightGraphics.clear();

    if (!this.currentSlot) return;

    const { centerX, centerY } = this.currentSlot;

    // 알파값 애니메이션 (부드러운 펄스)
    this.cornerAlpha += this.cornerAlphaDirection * 0.02;
    if (this.cornerAlpha <= 0.4) {
      this.cornerAlpha = 0.4;
      this.cornerAlphaDirection = 1;
    } else if (this.cornerAlpha >= 0.9) {
      this.cornerAlpha = 0.9;
      this.cornerAlphaDirection = -1;
    }

    const halfSize = TILE_SIZE / 2;
    const left = centerX - halfSize;
    const right = centerX + halfSize;
    const top = centerY - halfSize;
    const bottom = centerY + halfSize;

    // 코너 마커 크기 (타일의 25%)
    const cornerLen = TILE_SIZE * 0.25;
    const lineWidth = 2;

    // 상호작용 타입에 따른 색상
    const color = this.currentInteraction === 'harvest'
      ? 0xffd700  // 황금색 (수확)
      : this.currentInteraction === 'plant'
        ? 0x90ee90  // 연초록 (심기)
        : 0xffffff; // 흰색 (기본)

    this.highlightGraphics.lineStyle(lineWidth, color, this.cornerAlpha);

    // 좌상단 코너 ◤
    this.highlightGraphics.beginPath();
    this.highlightGraphics.moveTo(left, top + cornerLen);
    this.highlightGraphics.lineTo(left, top);
    this.highlightGraphics.lineTo(left + cornerLen, top);
    this.highlightGraphics.strokePath();

    // 우상단 코너 ◥
    this.highlightGraphics.beginPath();
    this.highlightGraphics.moveTo(right - cornerLen, top);
    this.highlightGraphics.lineTo(right, top);
    this.highlightGraphics.lineTo(right, top + cornerLen);
    this.highlightGraphics.strokePath();

    // 좌하단 코너 ◣
    this.highlightGraphics.beginPath();
    this.highlightGraphics.moveTo(left, bottom - cornerLen);
    this.highlightGraphics.lineTo(left, bottom);
    this.highlightGraphics.lineTo(left + cornerLen, bottom);
    this.highlightGraphics.strokePath();

    // 우하단 코너 ◢
    this.highlightGraphics.beginPath();
    this.highlightGraphics.moveTo(right - cornerLen, bottom);
    this.highlightGraphics.lineTo(right, bottom);
    this.highlightGraphics.lineTo(right, bottom - cornerLen);
    this.highlightGraphics.strokePath();
  }

  /**
   * 현재 상호작용 가능한 슬롯 인덱스
   */
  getCurrentSlot(): number | null {
    return this.currentSlot?.slot ?? null;
  }

  /**
   * 현재 상호작용 가능한 슬롯 정보
   */
  getCurrentSlotInfo(): SlotInteraction | null {
    return this.currentSlot;
  }

  /**
   * 현재 상호작용 타입
   */
  getCurrentInteraction(): InteractionType {
    return this.currentInteraction;
  }

  /**
   * 상호작용 가능 여부
   */
  canInteract(): boolean {
    return this.currentSlot !== null && this.currentInteraction !== 'none';
  }

  /**
   * 정리
   */
  destroy(): void {
    this.highlightGraphics.destroy();
    this.onInteractionChange = null;
  }
}
