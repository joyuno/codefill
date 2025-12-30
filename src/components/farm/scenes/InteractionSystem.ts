/**
 * InteractionSystem - 상호작용 시스템
 * 슬롯 하이라이트, 액션 인디케이터, 근처 슬롯 감지
 */

import Phaser from 'phaser';
import { TILE_SIZE, INTERACTION_RADIUS } from '../config/gameConfig';
import { DEPTH } from '../config/depthConfig';
import { CropManager, FarmSlotData } from './CropManager';
import { PlayerController } from './PlayerController';

// 상호작용 타입
export type InteractionType = 'plant' | 'harvest' | 'none';

export class InteractionSystem {
  private scene: Phaser.Scene;
  private cropManager: CropManager;
  private playerController: PlayerController;

  private highlightGraphics: Phaser.GameObjects.Graphics;
  private indicatorText: Phaser.GameObjects.Text;

  private currentSlot: number = -1;
  private currentInteraction: InteractionType = 'none';

  constructor(
    scene: Phaser.Scene,
    cropManager: CropManager,
    playerController: PlayerController
  ) {
    this.scene = scene;
    this.cropManager = cropManager;
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
   * 매 프레임 업데이트
   * @param selectedSeed 현재 선택된 씨앗 코드
   */
  update(selectedSeed: string | null): void {
    const playerPos = this.playerController.getPosition();
    const nearestSlot = this.findNearestSlot(playerPos.x, playerPos.y);

    if (nearestSlot !== this.currentSlot) {
      this.currentSlot = nearestSlot;
      this.updateHighlight();
    }

    // 상호작용 타입 결정
    if (nearestSlot >= 0) {
      const slotData = this.cropManager.getSlotData(nearestSlot);
      this.currentInteraction = this.determineInteraction(slotData, selectedSeed);
      this.updateIndicator(nearestSlot);
    } else {
      this.currentInteraction = 'none';
      this.hideIndicator();
    }
  }

  /**
   * 가장 가까운 슬롯 찾기
   */
  private findNearestSlot(playerX: number, playerY: number): number {
    const farmSize = this.cropManager.getFarmSize();
    let nearestSlot = -1;
    let nearestDistance = INTERACTION_RADIUS;

    for (let i = 0; i < farmSize * farmSize; i++) {
      const slotPos = this.cropManager.getSlotPosition(i);
      const distance = Phaser.Math.Distance.Between(
        playerX, playerY,
        slotPos.x, slotPos.y
      );

      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearestSlot = i;
      }
    }

    return nearestSlot;
  }

  /**
   * 상호작용 타입 결정
   */
  private determineInteraction(
    slotData: FarmSlotData | undefined,
    selectedSeed: string | null
  ): InteractionType {
    // 작물이 있고 수확 가능한 경우
    if (slotData?.cropCode && slotData.stage >= 4) {
      return 'harvest';
    }

    // 빈 슬롯이고 씨앗이 선택된 경우
    // slotData가 없어도 빈 슬롯으로 취급 (테스트/확장용)
    if ((!slotData || !slotData.cropCode) && selectedSeed) {
      return 'plant';
    }

    return 'none';
  }

  /**
   * 하이라이트 업데이트
   */
  private updateHighlight(): void {
    this.highlightGraphics.clear();

    if (this.currentSlot < 0) return;

    const pos = this.cropManager.getSlotPosition(this.currentSlot);

    // 노란색 테두리 하이라이트
    this.highlightGraphics.lineStyle(3, 0xffff00, 0.8);
    this.highlightGraphics.strokeRect(
      pos.x - TILE_SIZE / 2,
      pos.y - TILE_SIZE / 2,
      TILE_SIZE,
      TILE_SIZE
    );

    // 안쪽 약한 하이라이트
    this.highlightGraphics.fillStyle(0xffff00, 0.15);
    this.highlightGraphics.fillRect(
      pos.x - TILE_SIZE / 2,
      pos.y - TILE_SIZE / 2,
      TILE_SIZE,
      TILE_SIZE
    );
  }

  /**
   * 인디케이터 텍스트 업데이트
   */
  private updateIndicator(slotIndex: number): void {
    if (this.currentInteraction === 'none') {
      this.hideIndicator();
      return;
    }

    const pos = this.cropManager.getSlotPosition(slotIndex);
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
    this.indicatorText.setPosition(pos.x, pos.y - TILE_SIZE / 2 - 5);
    this.indicatorText.setVisible(true);
  }

  /**
   * 인디케이터 숨기기
   */
  private hideIndicator(): void {
    this.indicatorText.setVisible(false);
  }

  /**
   * 현재 상호작용 가능한 슬롯 번호
   */
  getCurrentSlot(): number {
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
    return this.currentSlot >= 0 && this.currentInteraction !== 'none';
  }

  /**
   * 정리
   */
  destroy(): void {
    this.highlightGraphics.destroy();
    this.indicatorText.destroy();
  }
}
