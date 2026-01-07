/**
 * FarmScene - Phaser 메인 농장 씬
 * 스타듀밸리 스타일 2D 농장 게임
 *
 * 통합 배치 시스템 리팩토링 - 레거시 매니저 제거됨
 *
 * 매니저 구성:
 * - MapManager: 바닥, 격자선
 * - PlayerController: 캐릭터 이동/애니메이션
 * - UnifiedPlacementManager: 모든 배치 아이템 (건물, 밭, 나무, 장식, 울타리, 작물)
 * - InteractionSystem: 하이라이트, 액션
 */

import Phaser from 'phaser';
import { MAP_WIDTH, MAP_HEIGHT, TILE_SIZE } from '../config/gameConfig';
import { MapManager } from './MapManager';
import { PlayerController } from './PlayerController';
import { InteractionSystem } from './InteractionSystem';
import { UnifiedPlacementManager } from './UnifiedPlacementManager';
import type { PlacedItem } from '@/lib/api/farm';

// 인벤토리 아이템 타입
interface InventoryItem {
  itemCode: string;
  quantity: number;
}

// 씬 초기화 데이터 (FarmGame.tsx에서 전달)
interface FarmSceneData {
  gold: number;
  farmSize: number;
  inventory: InventoryItem[];
  onNotify: (message: string, type: 'success' | 'error') => void;
  selectedSeed: string;
  // 통합 배치 시스템
  placedItems: PlacedItem[];
  onPlaceItemLocally: (itemCode: string, tileX: number, tileY: number) => string | null;
  onMoveItem: (itemId: string, tileX: number, tileY: number) => Promise<void>;
  onRemoveItem: (itemId: string) => Promise<void>;
  onPlantOnPlot: (plotId: string, cropCode: string) => Promise<void>;
  onHarvestFromPlot: (plotId: string) => Promise<{ gold: number; xp: number } | null>;
  selectedPlacementItem?: string | null;
  placementMode?: boolean;
  deleteMode?: boolean;
}

export class FarmScene extends Phaser.Scene {
  // 매니저들
  private mapManager!: MapManager;
  private playerController!: PlayerController;
  private interactionSystem!: InteractionSystem;
  private unifiedPlacementManager!: UnifiedPlacementManager;

  // 데이터
  private farmData!: FarmSceneData;
  private selectedSeed: string = '';
  private inventory: InventoryItem[] = [];

  // 배치 시스템 상태
  private placementMode: boolean = false;
  private selectedPlacementItem: string | null = null;
  private deleteMode: boolean = false;

  constructor() {
    super({ key: 'FarmScene' });
  }

  /**
   * 씬 초기화 - React에서 데이터 수신
   */
  init(data: FarmSceneData): void {
    this.farmData = data;
    this.selectedSeed = data.selectedSeed || '';
    this.inventory = data.inventory || [];
    this.placementMode = data.placementMode || false;
    this.selectedPlacementItem = data.selectedPlacementItem || null;
    this.deleteMode = data.deleteMode || false;
  }

  /**
   * 씨앗 보유량 확인
   */
  private getSeedCount(cropCode: string): number {
    const seedCode = `seed_${cropCode}`;
    const item = this.inventory.find(i => i.itemCode === seedCode);
    return item?.quantity || 0;
  }

  // ====== 공통 농작업 메서드 ======

  /**
   * 작물 심기 (공통 로직)
   */
  private async plantCrop(plotId: string, cropCode: string): Promise<boolean> {
    // 씨앗 보유량 체크
    const seedCount = this.getSeedCount(cropCode);
    if (seedCount <= 0) {
      this.farmData.onNotify('씨앗이 부족합니다!', 'error');
      return false;
    }

    try {
      await this.playerController.playHarvestAnimation();
      await this.farmData.onPlantOnPlot(plotId, cropCode);
      this.unifiedPlacementManager.updateCrop(plotId, cropCode, 1);
      return true;
    } catch {
      this.farmData.onNotify('심기에 실패했습니다', 'error');
      return false;
    }
  }

  /**
   * 작물 수확 (공통 로직)
   */
  private async harvestCrop(plotId: string): Promise<boolean> {
    try {
      await this.playerController.playHarvestAnimation();
      const result = await this.farmData.onHarvestFromPlot(plotId);
      if (result) {
        this.unifiedPlacementManager.updateCrop(plotId, '', 0);
        this.farmData.onNotify(`+${result.gold}G, +${result.xp}XP`, 'success');
        return true;
      }
      return false;
    } catch {
      this.farmData.onNotify('수확에 실패했습니다', 'error');
      return false;
    }
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    // 매니저 생성
    this.mapManager = new MapManager(this);
    this.playerController = new PlayerController(this);
    this.unifiedPlacementManager = new UnifiedPlacementManager(this);

    // 각 매니저 에셋 로드
    this.mapManager.preload();
    this.playerController.preload();
    this.unifiedPlacementManager.preload();
  }

  /**
   * 씬 생성
   */
  create(): void {
    // 카메라 설정 (고정 크기)
    this.cameras.main.setBounds(0, 0, MAP_WIDTH, MAP_HEIGHT);
    this.cameras.main.setBackgroundColor('#3d8b3d');

    // 순서대로 매니저 생성 (depth 순서 고려)
    this.mapManager.create();

    // 통합 배치 시스템 초기화
    this.unifiedPlacementManager.create();
    if (this.farmData.placedItems) {
      this.unifiedPlacementManager.loadItems(this.farmData.placedItems);
    }

    // 콜백 설정
    this.unifiedPlacementManager.setCallbacks({
      onMoveItem: this.farmData.onMoveItem,
      onRemoveItem: this.farmData.onRemoveItem,
      onPlantOnPlot: this.farmData.onPlantOnPlot,
      onHarvestFromPlot: this.farmData.onHarvestFromPlot,
    });

    this.playerController.create();

    // 상호작용 시스템 초기화
    this.interactionSystem = new InteractionSystem(
      this,
      this.playerController
    );
    // UnifiedPlacementManager 참조 전달
    this.interactionSystem.setUnifiedPlacementManager(this.unifiedPlacementManager);

    // 초기 배치 모드 적용
    if (this.placementMode) {
      this.unifiedPlacementManager.enableDragMode();
    }

    // 플레이어 액션 콜백 설정
    this.playerController.setActionCallback(() => this.handleAction());

    // 마우스 이벤트 설정
    this.setupMouseEvents();
  }

  /**
   * 마우스 이벤트 설정
   */
  private setupMouseEvents(): void {
    // 마우스 좌클릭
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      // 우클릭 무시 (별도 처리)
      if (pointer.rightButtonDown()) return;

      const tileX = Math.floor(pointer.worldX / TILE_SIZE);
      const tileY = Math.floor(pointer.worldY / TILE_SIZE);

      if (this.placementMode) {
        // 배치 모드: 좌클릭으로 아이템 배치 (로컬)
        if (this.selectedPlacementItem && this.farmData.onPlaceItemLocally) {
          const tempId = this.farmData.onPlaceItemLocally(this.selectedPlacementItem, tileX, tileY);
          if (tempId) {
            this.farmData.onNotify('아이템 배치됨 (저장 시 적용)', 'success');
          } else {
            this.farmData.onNotify('이 위치에는 배치할 수 없습니다', 'error');
          }
        }
      } else {
        // 씨앗 모드: 좌클릭으로 밭에 심기/수확 (마우스 조작)
        this.handleMouseAction(tileX, tileY);
      }
    });

    // 마우스 우클릭 (배치 모드에서 로컬 삭제)
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      if (!pointer.rightButtonDown()) return;
      if (!this.placementMode) return;

      const tileX = Math.floor(pointer.worldX / TILE_SIZE);
      const tileY = Math.floor(pointer.worldY / TILE_SIZE);

      // 해당 위치의 배치된 아이템 찾아서 로컬 삭제 (API 호출 없음)
      const item = this.unifiedPlacementManager.getItemAt(tileX, tileY);
      if (item) {
        const success = this.unifiedPlacementManager.deleteItemLocally(item.id);
        if (success) {
          this.farmData.onNotify('아이템 제거됨 (저장 시 적용)', 'success');
        } else {
          this.farmData.onNotify('이 아이템은 삭제할 수 없습니다', 'error');
        }
      }
    });

    // 우클릭 기본 동작 방지
    this.game.canvas.addEventListener('contextmenu', (e) => {
      e.preventDefault();
    });
  }

  /**
   * 마우스 클릭으로 밭 액션 처리 (씨앗 모드)
   */
  private async handleMouseAction(tileX: number, tileY: number): Promise<void> {
    // 해당 위치에 밭이 있는지 확인
    const plot = this.unifiedPlacementManager.getFarmPlotAt(tileX, tileY);
    if (!plot) return;

    // 플레이어가 액션 중이면 무시
    if (this.playerController.isPerformingAction()) return;

    const plotData = plot.data as { cropCode?: string; stage?: number } | undefined;

    if (plotData?.cropCode && plotData?.stage === 4) {
      // 수확 가능한 작물이 있으면 수확
      await this.harvestCrop(plot.id);
    } else if (!plotData?.cropCode && this.selectedSeed) {
      // 빈 밭이고 씨앗이 선택되어 있으면 심기
      await this.plantCrop(plot.id, this.selectedSeed);
    }
  }

  /**
   * 매 프레임 업데이트
   */
  update(): void {
    // 배치 모드가 아닐 때만 플레이어 컨트롤러 업데이트
    if (!this.placementMode) {
      this.playerController.update();
      this.interactionSystem.update(this.selectedSeed);
    }
    // 작물 타이머 업데이트는 UnifiedPlacementManager에서 처리
    this.unifiedPlacementManager.update();
  }

  /**
   * 액션 처리 (SPACE 키)
   */
  private async handleAction(): Promise<void> {
    // 배치 모드에서는 액션 처리 안함
    if (this.placementMode) return;
    if (!this.interactionSystem.canInteract()) return;
    if (this.playerController.isPerformingAction()) return;

    const interaction = this.interactionSystem.getCurrentInteraction();
    const currentPlot = this.interactionSystem.getCurrentPlot();

    if (!currentPlot) return;

    if (interaction === 'plant' && this.selectedSeed) {
      await this.plantCrop(currentPlot.id, this.selectedSeed);
    } else if (interaction === 'harvest') {
      // 수확 가능 여부 체크
      const plotData = currentPlot.data as { cropCode?: string; stage?: number } | undefined;
      if (!plotData?.cropCode) {
        this.farmData.onNotify('수확할 작물이 없습니다!', 'error');
        return;
      }
      if ((plotData.stage || 0) < 4) {
        this.farmData.onNotify('아직 다 자라지 않았습니다!', 'error');
        return;
      }
      await this.harvestCrop(currentPlot.id);
    }
  }

  /**
   * 외부에서 데이터 업데이트 (React → Phaser)
   */
  updateFarmData(selectedSeed: string, inventory?: InventoryItem[]): void {
    this.selectedSeed = selectedSeed;

    if (inventory) {
      this.inventory = inventory;
    }
  }

  /**
   * 배치 모드 업데이트 (React → Phaser)
   */
  updatePlacementMode(enabled: boolean, deleteMode: boolean): void {
    this.placementMode = enabled;
    this.deleteMode = deleteMode;

    if (enabled) {
      this.unifiedPlacementManager.enableDragMode();
    } else {
      this.unifiedPlacementManager.disableDragMode();
    }
  }

  // ====== 통합 배치 시스템 메서드 ======

  /**
   * 배치된 아이템 업데이트 (React → Phaser)
   */
  updatePlacedItems(items: PlacedItem[]): void {
    // 드래그 중이면 스킵 (드래그 완료 후 자동 동기화됨)
    if (this.unifiedPlacementManager.isDragging()) {
      return;
    }

    this.unifiedPlacementManager.loadItems(items);

    // 현재 배치 모드라면 드래그 모드 활성화
    if (this.placementMode) {
      this.unifiedPlacementManager.enableDragMode();
    }
  }

  /**
   * 선택된 배치 아이템 업데이트 (React → Phaser)
   */
  updateSelectedPlacementItem(itemCode: string | null): void {
    this.selectedPlacementItem = itemCode;
  }

  /**
   * 아이템 추가
   */
  addPlacedItem(item: PlacedItem): void {
    this.unifiedPlacementManager.addItem(item);
  }

  /**
   * 아이템 제거
   */
  removePlacedItem(itemId: string): void {
    this.unifiedPlacementManager.removeItem(itemId);
  }

  /**
   * 작물 업데이트
   */
  updateCropOnPlot(plotId: string, cropCode: string | null, stage: number): void {
    this.unifiedPlacementManager.updateCrop(plotId, cropCode, stage);
  }

  /**
   * 배치 가능 여부 확인
   */
  canPlaceAt(tileX: number, tileY: number, width: number, height: number): boolean {
    return this.unifiedPlacementManager.canPlaceAt(tileX, tileY, width, height);
  }

  /**
   * 아이템 로컬 배치 (API 호출 없음)
   */
  placeItemLocally(itemCode: string, tileX: number, tileY: number, metadata: PlacedItem['metadata']): string | null {
    return this.unifiedPlacementManager.placeItemLocally(itemCode, tileX, tileY, metadata);
  }

  // ====== 배치 모드 저장/취소 메서드 ======

  /**
   * 배치 변경 사항이 있는지 확인
   */
  hasPlacementChanges(): boolean {
    return this.unifiedPlacementManager.hasChanges();
  }

  /**
   * 배치 변경 사항 가져오기
   */
  getPlacementChanges() {
    return this.unifiedPlacementManager.getChanges();
  }

  /**
   * 배치 변경 사항 취소 (원래 상태로 복원)
   */
  revertPlacementChanges(): void {
    this.unifiedPlacementManager.revertChanges();
  }

  /**
   * 배치 변경 사항 확정 (저장 성공 후 호출)
   */
  confirmPlacementChanges(): void {
    this.unifiedPlacementManager.clearChanges();
  }

  /**
   * 씬 정리
   */
  shutdown(): void {
    this.mapManager?.destroy();
    this.playerController?.destroy();
    this.interactionSystem?.destroy();
    this.unifiedPlacementManager?.destroy();
  }
}
