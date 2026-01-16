/**
 * InteractionSystem - 상호작용 시스템
 * 슬롯 하이라이트, 액션 인디케이터, 근처 밭 슬롯 감지
 *
 * 리팩토링: farm_plot → slot 기반 시스템
 */

import * as Phaser from 'phaser';
import { TILE_SIZE, INTERACTION_RADIUS } from '../config/gameConfig';
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

export class InteractionSystem {
  private scene: Phaser.Scene;
  private playerController: PlayerController;
  private farmGridManager: FarmGridManager | null = null;

  private highlightGraphics: Phaser.GameObjects.Graphics;
  private indicatorText: Phaser.GameObjects.Text;

  private currentSlot: SlotInteraction | null = null;
  private currentInteraction: InteractionType = 'none';

  // 현재 farm_slots 데이터 (FarmScene에서 업데이트)
  private farmSlots: FarmSlot[] = [];

  constructor(
    scene: Phaser.Scene,
    playerController: PlayerController
  ) {
    this.scene = scene;
    this.playerController = playerController;

    // 하이라이트 그래픽스
    this.highlightGraphics = scene.add.graphics();
    this.highlightGraphics.setDepth(DEPTH.HIGHLIGHT);

    // 인디케이터 텍스트
    this.indicatorText = scene.add.text(0, 0, '', {
      fontSize: '14px',
      fontFamily: 'Arial',
      color: '#ffffff',
      backgroundColor: '#000000aa',
      padding: { x: 8, y: 4 },
    });
    this.indicatorText.setOrigin(0.5, 1);
    this.indicatorText.setDepth(DEPTH.INDICATOR);
    this.indicatorText.setVisible(false);
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

    if (nearestSlot?.slot !== this.currentSlot?.slot) {
      this.currentSlot = nearestSlot;
      this.updateHighlight();
    }

    // 상호작용 타입 결정
    if (nearestSlot) {
      this.currentInteraction = this.determineInteraction(nearestSlot.slotData, selectedSeed);
      this.updateIndicator(nearestSlot);
    } else {
      this.currentInteraction = 'none';
      this.hideIndicator();
    }
  }

  /**
   * 가장 가까운 밭 슬롯 찾기
   */
  private findNearestSlot(playerX: number, playerY: number): SlotInteraction | null {
    if (!this.farmGridManager) return null;

    const farmSize = this.farmGridManager.getFarmSize();
    if (farmSize === 0) return null;

    let nearestSlot: SlotInteraction | null = null;
    let nearestDistance = INTERACTION_RADIUS;

    for (let i = 0; i < farmSize; i++) {
      const center = this.farmGridManager.getSlotCenter(i);
      if (!center) continue;

      const distance = Phaser.Math.Distance.Between(
        playerX, playerY,
        center.x, center.y
      );

      if (distance < nearestDistance) {
        nearestDistance = distance;
        const slotData = this.farmSlots.find(s => s.slot === i) || {
          slot: i,
          cropCode: null,
          plantedAt: null,
          growTimeSeconds: null,
          stage: 0,
        };
        nearestSlot = {
          slot: i,
          slotData,
          centerX: center.x,
          centerY: center.y,
        };
      }
    }

    return nearestSlot;
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
   * 하이라이트 업데이트
   */
  private updateHighlight(): void {
    this.highlightGraphics.clear();

    if (!this.currentSlot) return;

    const { centerX, centerY } = this.currentSlot;

    // 노란색 테두리 하이라이트
    this.highlightGraphics.lineStyle(3, 0xffff00, 0.8);
    this.highlightGraphics.strokeRect(
      centerX - TILE_SIZE / 2,
      centerY - TILE_SIZE / 2,
      TILE_SIZE,
      TILE_SIZE
    );

    // 안쪽 약한 하이라이트
    this.highlightGraphics.fillStyle(0xffff00, 0.15);
    this.highlightGraphics.fillRect(
      centerX - TILE_SIZE / 2,
      centerY - TILE_SIZE / 2,
      TILE_SIZE,
      TILE_SIZE
    );
  }

  /**
   * 인디케이터 텍스트 업데이트
   */
  private updateIndicator(slotInfo: SlotInteraction): void {
    if (this.currentInteraction === 'none') {
      this.hideIndicator();
      return;
    }

    const { centerX, centerY } = slotInfo;
    let text = '';

    switch (this.currentInteraction) {
      case 'plant':
        text = 'SPACE: 심기';
        break;
      case 'harvest':
        text = 'SPACE: 수확';
        break;
    }

    this.indicatorText.setText(text);
    this.indicatorText.setPosition(centerX, centerY - TILE_SIZE / 2 - 5);
    this.indicatorText.setVisible(true);
  }

  /**
   * 인디케이터 숨기기
   */
  private hideIndicator(): void {
    this.indicatorText.setVisible(false);
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
    this.indicatorText.destroy();
  }
}
