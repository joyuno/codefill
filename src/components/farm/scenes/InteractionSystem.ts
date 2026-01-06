/**
 * InteractionSystem - 상호작용 시스템
 * 슬롯 하이라이트, 액션 인디케이터, 근처 밭(farm_plot) 감지
 *
 * 통합 배치 시스템 리팩토링 - CropManager 제거됨
 */

import Phaser from 'phaser';
import { TILE_SIZE, INTERACTION_RADIUS } from '../config/gameConfig';
import { DEPTH } from '../config/depthConfig';
import { PlayerController } from './PlayerController';
import type { UnifiedPlacementManager } from './UnifiedPlacementManager';
import type { PlacedItem } from '@/lib/api/farm';

// 상호작용 타입
export type InteractionType = 'plant' | 'harvest' | 'none';

export class InteractionSystem {
  private scene: Phaser.Scene;
  private playerController: PlayerController;
  private unifiedPlacementManager: UnifiedPlacementManager | null = null;

  private highlightGraphics: Phaser.GameObjects.Graphics;
  private indicatorText: Phaser.GameObjects.Text;

  private currentPlot: PlacedItem | null = null;
  private currentInteraction: InteractionType = 'none';

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
   * UnifiedPlacementManager 설정
   */
  setUnifiedPlacementManager(manager: UnifiedPlacementManager): void {
    this.unifiedPlacementManager = manager;
  }

  /**
   * 매 프레임 업데이트
   * @param selectedSeed 현재 선택된 씨앗 코드
   */
  update(selectedSeed: string | null): void {
    if (!this.unifiedPlacementManager) return;

    const playerPos = this.playerController.getPosition();
    const nearestPlot = this.findNearestFarmPlot(playerPos.x, playerPos.y);

    if (nearestPlot?.id !== this.currentPlot?.id) {
      this.currentPlot = nearestPlot;
      this.updateHighlight();
    }

    // 상호작용 타입 결정
    if (nearestPlot) {
      this.currentInteraction = this.determineInteraction(nearestPlot, selectedSeed);
      this.updateIndicator(nearestPlot);
    } else {
      this.currentInteraction = 'none';
      this.hideIndicator();
    }
  }

  /**
   * 가장 가까운 farm_plot 찾기
   */
  private findNearestFarmPlot(playerX: number, playerY: number): PlacedItem | null {
    if (!this.unifiedPlacementManager) return null;

    const farmPlots = this.unifiedPlacementManager.getFarmPlots();
    let nearestPlot: PlacedItem | null = null;
    let nearestDistance = INTERACTION_RADIUS;

    for (const plot of farmPlots) {
      // 타일 중심 좌표 계산
      const plotCenterX = plot.tileX * TILE_SIZE + TILE_SIZE / 2;
      const plotCenterY = plot.tileY * TILE_SIZE + TILE_SIZE / 2;

      const distance = Phaser.Math.Distance.Between(
        playerX, playerY,
        plotCenterX, plotCenterY
      );

      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearestPlot = plot;
      }
    }

    return nearestPlot;
  }

  /**
   * 상호작용 타입 결정
   */
  private determineInteraction(
    plot: PlacedItem,
    selectedSeed: string | null
  ): InteractionType {
    const plotData = plot.data as { cropCode?: string; stage?: number } | undefined;

    // 작물이 있고 수확 가능한 경우 (stage >= 4)
    if (plotData?.cropCode && (plotData.stage || 0) >= 4) {
      return 'harvest';
    }

    // 빈 밭이고 씨앗이 선택된 경우
    if (!plotData?.cropCode && selectedSeed) {
      return 'plant';
    }

    return 'none';
  }

  /**
   * 하이라이트 업데이트
   */
  private updateHighlight(): void {
    this.highlightGraphics.clear();

    if (!this.currentPlot) return;

    const centerX = this.currentPlot.tileX * TILE_SIZE + TILE_SIZE / 2;
    const centerY = this.currentPlot.tileY * TILE_SIZE + TILE_SIZE / 2;

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
  private updateIndicator(plot: PlacedItem): void {
    if (this.currentInteraction === 'none') {
      this.hideIndicator();
      return;
    }

    const centerX = plot.tileX * TILE_SIZE + TILE_SIZE / 2;
    const centerY = plot.tileY * TILE_SIZE + TILE_SIZE / 2;
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
   * 현재 상호작용 가능한 밭 (farm_plot)
   */
  getCurrentPlot(): PlacedItem | null {
    return this.currentPlot;
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
    return this.currentPlot !== null && this.currentInteraction !== 'none';
  }

  /**
   * 정리
   */
  destroy(): void {
    this.highlightGraphics.destroy();
    this.indicatorText.destroy();
  }
}
