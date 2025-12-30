/**
 * FarmScene - Phaser 메인 농장 씬
 * 스타듀밸리 스타일 2D 농장 게임
 *
 * 각 매니저에게 책임을 위임:
 * - MapManager: 바닥, 격자선, 장식
 * - PlayerController: 캐릭터 이동/애니메이션
 * - CropManager: 밭, 작물 렌더링
 * - BuildingManager: 건물 배치
 * - InteractionSystem: 하이라이트, 액션
 */

import Phaser from 'phaser';
import { MAP_WIDTH, MAP_HEIGHT } from '../config/gameConfig';
import { MapManager } from './MapManager';
import { PlayerController } from './PlayerController';
import { CropManager, FarmSlotData } from './CropManager';
import { BuildingManager } from './BuildingManager';
import { InteractionSystem } from './InteractionSystem';

// 인벤토리 아이템 타입
interface InventoryItem {
  itemCode: string;
  quantity: number;
}

// 씬 초기화 데이터 (FarmGame.tsx에서 전달)
interface FarmSceneData {
  gold: number;
  farmSize: number;
  farmSlots: FarmSlotData[];
  inventory: InventoryItem[];
  onPlant: (slot: number, cropCode: string) => Promise<void>;
  onHarvest: (slot: number) => Promise<void>;
  onNotify: (message: string, type: 'success' | 'error') => void;
  selectedSeed: string;
}

export class FarmScene extends Phaser.Scene {
  // 매니저들
  private mapManager!: MapManager;
  private playerController!: PlayerController;
  private cropManager!: CropManager;
  private buildingManager!: BuildingManager;
  private interactionSystem!: InteractionSystem;

  // 데이터
  private farmData!: FarmSceneData;
  private selectedSeed: string = '';
  private inventory: InventoryItem[] = [];

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
  }

  /**
   * 씨앗 보유량 확인
   */
  private getSeedCount(cropCode: string): number {
    const seedCode = `seed_${cropCode}`;
    const item = this.inventory.find(i => i.itemCode === seedCode);
    return item?.quantity || 0;
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    // 매니저 생성
    this.mapManager = new MapManager(this);
    this.playerController = new PlayerController(this);
    this.cropManager = new CropManager(this);
    this.buildingManager = new BuildingManager(this);

    // 각 매니저 에셋 로드
    this.mapManager.preload();
    this.playerController.preload();
    this.cropManager.preload();
    this.buildingManager.preload();
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
    this.cropManager.create(this.farmData.farmSize);
    this.buildingManager.create();
    this.playerController.create();

    // 상호작용 시스템 초기화 (player, crop 매니저 필요)
    this.interactionSystem = new InteractionSystem(
      this,
      this.cropManager,
      this.playerController
    );

    // 초기 작물 데이터 로드
    if (this.farmData.farmSlots) {
      this.cropManager.updateFarmData(this.farmData.farmSlots);
    }

    // 플레이어 액션 콜백 설정
    this.playerController.setActionCallback(() => this.handleAction());
  }

  /**
   * 매 프레임 업데이트
   */
  update(): void {
    this.playerController.update();
    this.interactionSystem.update(this.selectedSeed);
    this.cropManager.update();  // 타이머 업데이트
  }

  /**
   * 액션 처리 (SPACE 키)
   */
  private async handleAction(): Promise<void> {
    if (!this.interactionSystem.canInteract()) return;
    if (this.playerController.isPerformingAction()) return;

    const slot = this.interactionSystem.getCurrentSlot();
    const interaction = this.interactionSystem.getCurrentInteraction();

    try {
      if (interaction === 'plant' && this.selectedSeed) {
        // 씨앗 체크 먼저! (애니메이션 전에)
        const seedCount = this.getSeedCount(this.selectedSeed);
        if (seedCount <= 0) {
          this.farmData.onNotify('씨앗이 부족합니다!', 'error');
          return;
        }

        // 심기 애니메이션 + API 호출
        await this.playerController.playHarvestAnimation();
        await this.farmData.onPlant(slot, this.selectedSeed);

        // 로컬 업데이트 (API 응답 전 즉시 표시)
        this.cropManager.updateSlot(slot, this.selectedSeed, 0);

      } else if (interaction === 'harvest') {
        // 수확 가능 여부 체크
        const slotData = this.cropManager.getSlotData(slot);
        if (!slotData || !slotData.cropCode) {
          this.farmData.onNotify('수확할 작물이 없습니다!', 'error');
          return;
        }
        if (slotData.stage < 4) {
          this.farmData.onNotify('아직 다 자라지 않았습니다!', 'error');
          return;
        }

        // 수확 애니메이션 + API 호출
        await this.playerController.playHarvestAnimation();
        this.cropManager.playHarvestEffect(slot);
        await this.farmData.onHarvest(slot);

        // 작물 제거
        this.cropManager.updateSlot(slot, null, 0);
      }
    } catch (error) {
      console.error('Action failed:', error);
      this.farmData.onNotify('작업에 실패했습니다', 'error');
    }
  }

  /**
   * 외부에서 농장 데이터 업데이트 (React → Phaser)
   */
  updateFarmData(farmSlots: FarmSlotData[], selectedSeed: string, inventory?: InventoryItem[]): void {
    this.selectedSeed = selectedSeed;

    if (inventory) {
      this.inventory = inventory;
    }

    if (farmSlots) {
      this.cropManager.updateFarmData(farmSlots);
    }
  }

  /**
   * 농장 크기 변경
   */
  updateFarmSize(newSize: number): void {
    this.cropManager.setFarmSize(newSize);
  }

  /**
   * 씬 정리
   */
  shutdown(): void {
    this.mapManager?.destroy();
    this.playerController?.destroy();
    this.cropManager?.destroy();
    this.buildingManager?.destroy();
    this.interactionSystem?.destroy();
  }
}
