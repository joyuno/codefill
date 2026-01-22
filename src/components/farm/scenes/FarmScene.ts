/**
 * FarmScene - Phaser 메인 농장 씬
 * 스타듀밸리 스타일 2D 농장 게임
 *
 * 리팩토링: 그리드 기반 밭 시스템
 *
 * 매니저 구성:
 * - MapManager: 바닥, 격자선
 * - PlayerController: 캐릭터 이동/애니메이션
 * - FarmGridManager: 밭 그리드 및 작물
 * - UnifiedPlacementManager: 건물, 나무, 장식, 울타리
 * - InteractionSystem: 하이라이트, 액션
 */

import * as Phaser from 'phaser';
import { MAP_WIDTH, MAP_HEIGHT, TILE_SIZE } from '../config/gameConfig';
import { MapManager } from './MapManager';
import { PlayerController } from './PlayerController';
import { InteractionSystem, type InteractionCallback } from './InteractionSystem';
import { UnifiedPlacementManager } from './UnifiedPlacementManager';
import { FarmGridManager, FarmSlot } from './FarmGridManager';
import type { PlacedItem, CharacterData } from '@/lib/api/farm';

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
  // 캐릭터 데이터 (레이어 기반 렌더링용)
  characterData?: CharacterData | null;
  // 통합 배치 시스템
  placedItems: PlacedItem[];
  onPlaceItemLocally: (itemCode: string, tileX: number, tileY: number) => Promise<string | null>;
  onMoveItem: (itemId: string, tileX: number, tileY: number) => Promise<void>;
  onRemoveItem: (itemId: string) => Promise<void>;
  // 슬롯 기반 밭 시스템
  farmSlots: FarmSlot[];
  onPlantOnSlot: (slot: number, cropCode: string) => Promise<FarmSlot | null>;
  onHarvestFromSlot: (slot: number) => Promise<{ gold: number; xp: number; slot: FarmSlot } | null>;
  selectedPlacementItem?: string | null;
  placementMode?: boolean;
  deleteMode?: boolean;
  // 상호작용 상태 변경 콜백 (React UI 업데이트용)
  onInteractionChange?: InteractionCallback;
}

export class FarmScene extends Phaser.Scene {
  // 매니저들
  private mapManager!: MapManager;
  private playerController!: PlayerController;
  private interactionSystem!: InteractionSystem;
  private unifiedPlacementManager!: UnifiedPlacementManager;
  private farmGridManager!: FarmGridManager;

  // 데이터
  private farmData!: FarmSceneData;
  private selectedSeed: string = '';
  private inventory: InventoryItem[] = [];
  private farmSlots: FarmSlot[] = [];
  private farmSize: number = 1;

  // 배치 시스템 상태
  private placementMode: boolean = false;
  private selectedPlacementItem: string | null = null;
  private deleteMode: boolean = false;

  // 디버그 모드
  private debugMode: boolean = false;
  private debugKey: Phaser.Input.Keyboard.Key | null = null;
  private playerDebugGraphics: Phaser.GameObjects.Graphics | null = null;
  private playerDebugText: Phaser.GameObjects.Text | null = null;

  // 농작업 처리 중 플래그 (연속 클릭 방지)
  private isProcessingFarmAction: boolean = false;

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
    this.farmSlots = data.farmSlots || [];
    this.farmSize = data.farmSize || 1;
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

  // ====== 슬롯 기반 농작업 메서드 ======

  /**
   * 작물 심기 (슬롯 기반)
   * Optimistic Update 적용 - 즉시 씨앗(stage 0) 표시, 타이머는 API 응답 후
   */
  private async plantCrop(slot: number, cropCode: string): Promise<boolean> {
    // 연속 클릭 방지
    if (this.isProcessingFarmAction) return false;
    this.isProcessingFarmAction = true;

    // 씨앗 보유량 체크
    const seedCount = this.getSeedCount(cropCode);
    if (seedCount <= 0) {
      this.farmData.onNotify('씨앗이 부족합니다!', 'error');
      this.isProcessingFarmAction = false;
      return false;
    }

    const slotIndex = this.farmSlots.findIndex(s => s.slot === slot);

    // Optimistic Update - 즉시 씨앗 표시 (stage 0, 타이머 없음)
    const optimisticSlot = {
      slot,
      cropCode,
      stage: 0,  // 씨앗 상태
      plantedAt: null,  // 타이머 표시 안함
      growTimeSeconds: null,
    };

    if (slotIndex >= 0) {
      this.farmSlots[slotIndex] = optimisticSlot;
    } else {
      this.farmSlots.push(optimisticSlot);
    }
    this.farmGridManager.updateSlot(slot, optimisticSlot);

    try {
      // 애니메이션과 API 호출 병렬 실행
      const [, result] = await Promise.all([
        this.playerController.playDigAnimation(),
        this.farmData.onPlantOnSlot(slot, cropCode),
      ]);

      if (result) {
        // API 성공 - 서버 응답으로 타이머 포함 업데이트
        const newSlotIndex = this.farmSlots.findIndex(s => s.slot === slot);
        if (newSlotIndex >= 0) {
          this.farmSlots[newSlotIndex] = result;
        }
        this.farmGridManager.updateSlot(slot, result);
        this.interactionSystem.updateFarmSlots(this.farmSlots);
        this.isProcessingFarmAction = false;
        return true;
      }

      // API 실패 - 롤백
      this.rollbackSlot(slot, slotIndex);
      this.isProcessingFarmAction = false;
      return false;
    } catch (err) {
      console.error('[FarmScene] plantCrop error:', err);
      this.rollbackSlot(slot, slotIndex);
      this.farmData.onNotify('심기에 실패했습니다', 'error');
      this.isProcessingFarmAction = false;
      return false;
    }
  }

  /**
   * 슬롯 롤백 헬퍼
   */
  private rollbackSlot(slot: number, originalIndex: number): void {
    if (originalIndex >= 0) {
      // 기존 슬롯이었으면 빈 상태로
      const emptySlot = { slot, cropCode: null, stage: 0, plantedAt: null, growTimeSeconds: null };
      this.farmSlots[originalIndex] = emptySlot;
      this.farmGridManager.updateSlot(slot, emptySlot);
    } else {
      // 새로 추가된 슬롯이면 제거
      const idx = this.farmSlots.findIndex(s => s.slot === slot);
      if (idx >= 0) {
        this.farmSlots.splice(idx, 1);
        this.farmGridManager.updateSlot(slot, { slot, cropCode: null, stage: 0, plantedAt: null, growTimeSeconds: null });
      }
    }
    this.interactionSystem.updateFarmSlots(this.farmSlots);
  }

  /**
   * 작물 수확 (슬롯 기반)
   * Optimistic Update 적용 - 즉시 작물 제거 후 API 호출
   */
  private async harvestCrop(slot: number): Promise<boolean> {
    // 연속 클릭 방지
    if (this.isProcessingFarmAction) return false;
    this.isProcessingFarmAction = true;

    const slotIndex = this.farmSlots.findIndex(s => s.slot === slot);
    if (slotIndex < 0) {
      this.isProcessingFarmAction = false;
      return false;
    }

    // 현재 상태 백업 (롤백용)
    const originalSlot = { ...this.farmSlots[slotIndex] };

    // Optimistic Update - 즉시 UI에서 작물 제거
    const emptySlot = {
      slot,
      cropCode: null,
      stage: 0,
      plantedAt: null,
      growTimeSeconds: null,
    };
    this.farmSlots[slotIndex] = emptySlot;
    this.farmGridManager.updateSlot(slot, emptySlot);

    try {
      // 애니메이션과 API 호출 병렬 실행
      const [, result] = await Promise.all([
        this.playerController.playHarvestAnimation(),
        this.farmData.onHarvestFromSlot(slot),
      ]);

      if (result) {
        this.farmData.onNotify(`+${result.gold}G, +${result.xp}XP`, 'success');
        this.isProcessingFarmAction = false;
        return true;
      }

      // API 실패 - 롤백
      this.farmSlots[slotIndex] = originalSlot;
      this.farmGridManager.updateSlot(slot, originalSlot);
      this.isProcessingFarmAction = false;
      return false;
    } catch {
      // 에러 - 롤백
      this.farmSlots[slotIndex] = originalSlot;
      this.farmGridManager.updateSlot(slot, originalSlot);
      this.farmData.onNotify('수확에 실패했습니다', 'error');
      this.isProcessingFarmAction = false;
      return false;
    }
  }

  /**
   * 에셋 프리로드 (지연 로딩 적용)
   */
  preload(): void {
    // 매니저 생성 (PlayerController에 characterData 전달)
    this.mapManager = new MapManager(this);
    this.playerController = new PlayerController(this, this.farmData.characterData);
    this.unifiedPlacementManager = new UnifiedPlacementManager(this);
    this.farmGridManager = new FarmGridManager(this);

    // 각 매니저 에셋 로드 (지연 로딩: 필요한 것만)
    this.mapManager.preload();
    this.playerController.preload();

    // 배치된 아이템만 로드
    this.unifiedPlacementManager.preload(this.farmData.placedItems);

    // 심어진 작물 + 보유 씨앗만 로드
    this.farmGridManager.preload(this.farmSlots, this.inventory);
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

    // 밭 그리드 렌더링
    this.farmGridManager.renderGrid(this.farmSize, this.farmSlots);

    // 통합 배치 시스템 초기화 (건물, 나무, 장식)
    this.unifiedPlacementManager.create();
    if (this.farmData.placedItems) {
      this.unifiedPlacementManager.loadItems(this.farmData.placedItems);
    }

    // 콜백 설정 (farm_plot 관련 콜백 제거)
    this.unifiedPlacementManager.setCallbacks({
      onMoveItem: this.farmData.onMoveItem,
      onRemoveItem: this.farmData.onRemoveItem,
    });

    this.playerController.create();

    // 상호작용 시스템 초기화
    this.interactionSystem = new InteractionSystem(
      this,
      this.playerController
    );
    // FarmGridManager 참조 전달
    this.interactionSystem.setFarmGridManager(this.farmGridManager);
    this.interactionSystem.updateFarmSlots(this.farmSlots);
    // React 콜백 설정 (액션 프롬프트 UI용)
    if (this.farmData.onInteractionChange) {
      this.interactionSystem.setInteractionCallback(this.farmData.onInteractionChange);
    }

    // 초기 배치 모드 적용
    if (this.placementMode) {
      this.unifiedPlacementManager.enableDragMode();
    }

    // 플레이어 액션 콜백 설정
    this.playerController.setActionCallback(() => this.handleAction());

    // 플레이어 충돌 체크 설정 (건물/장애물)
    this.playerController.setCollisionChecker((tileX, tileY) =>
      this.unifiedPlacementManager.isTileBlocked(tileX, tileY)
    );

    // 마우스 이벤트 설정
    this.setupMouseEvents();

    // 디버그 키 설정 (` 백틱 키로 토글)
    if (this.input.keyboard) {
      this.debugKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.BACKTICK);
    }
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
          this.farmData.onPlaceItemLocally(this.selectedPlacementItem, tileX, tileY).then(tempId => {
            if (tempId) {
              this.farmData.onNotify('아이템 배치됨 (저장 시 적용)', 'success');
            } else {
              this.farmData.onNotify('이 위치에는 배치할 수 없습니다', 'error');
            }
          });
        }
      } else {
        // 씨앗 모드: 좌클릭으로 밭에 심기/수확 (마우스 조작)
        this.handleMouseAction(pointer.worldX, pointer.worldY);
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
  private async handleMouseAction(worldX: number, worldY: number): Promise<void> {
    // 해당 위치에 밭 슬롯이 있는지 확인
    const slot = this.farmGridManager.getSlotAt(worldX, worldY);
    if (slot === null) return;

    // 플레이어가 액션 중이면 무시
    if (this.playerController.isPerformingAction()) return;

    const slotData = this.farmSlots.find(s => s.slot === slot);

    if (slotData?.cropCode && slotData.stage >= 6) {
      // 수확 가능한 작물이 있으면 수확
      await this.harvestCrop(slot);
    } else if (!slotData?.cropCode && this.selectedSeed) {
      // 빈 밭이고 씨앗이 선택되어 있으면 심기
      await this.plantCrop(slot, this.selectedSeed);
    }
  }

  /**
   * 매 프레임 업데이트
   */
  update(): void {
    // 디버그 키 입력 처리 (` 백틱)
    if (this.debugKey && Phaser.Input.Keyboard.JustDown(this.debugKey)) {
      this.toggleDebugMode();
    }

    // 배치 모드가 아닐 때만 플레이어 컨트롤러 업데이트
    if (!this.placementMode) {
      this.playerController.update();
      this.interactionSystem.update(this.selectedSeed);
    }
    // 작물 타이머 업데이트
    this.farmGridManager.updateTimers(this.farmSlots);
    // 배치 시스템 업데이트 (호환성 유지)
    this.unifiedPlacementManager.update();

    // 디버그 모드일 때 충돌 표시 업데이트
    if (this.debugMode) {
      this.unifiedPlacementManager.updateCollisionDebug();
      this.updatePlayerDebug();
    }
  }

  /**
   * 디버그 모드 토글
   */
  private toggleDebugMode(): void {
    this.debugMode = !this.debugMode;

    if (this.debugMode) {
      // 디버그 모드 ON
      this.mapManager.showDebugGrid();
      this.unifiedPlacementManager.showCollisionDebug();

      // 플레이어 디버그 그래픽스 생성
      if (!this.playerDebugGraphics) {
        this.playerDebugGraphics = this.add.graphics();
        this.playerDebugGraphics.setDepth(600);
      }
      if (!this.playerDebugText) {
        this.playerDebugText = this.add.text(10, 10, '', {
          fontSize: '12px',
          color: '#00ff00',
          backgroundColor: '#000000',
          padding: { x: 5, y: 3 },
        });
        this.playerDebugText.setDepth(600);
        this.playerDebugText.setScrollFactor(0); // UI로 고정
      }

      this.farmData.onNotify('디버그 모드 ON (` 키로 토글)', 'success');
    } else {
      // 디버그 모드 OFF
      this.mapManager.hideDebugGrid();
      this.unifiedPlacementManager.hideCollisionDebug();

      // 플레이어 디버그 숨기기
      if (this.playerDebugGraphics) {
        this.playerDebugGraphics.clear();
      }
      if (this.playerDebugText) {
        this.playerDebugText.setVisible(false);
      }

      this.farmData.onNotify('디버그 모드 OFF', 'success');
    }
  }

  /**
   * 플레이어 디버그 정보 업데이트
   */
  private updatePlayerDebug(): void {
    if (!this.playerDebugGraphics || !this.playerDebugText) return;

    const pos = this.playerController.getPosition();
    const tileX = Math.floor(pos.x / TILE_SIZE);
    const tileY = Math.floor(pos.y / TILE_SIZE);
    const isBlocked = this.unifiedPlacementManager.isTileBlocked(tileX, tileY);

    // 플레이어 현재 타일 표시 (파란색/마젠타)
    this.playerDebugGraphics.clear();

    // 플레이어가 서있는 타일
    const color = isBlocked ? 0xff00ff : 0x0088ff; // 충돌이면 마젠타, 아니면 파랑
    this.playerDebugGraphics.fillStyle(color, 0.4);
    this.playerDebugGraphics.fillRect(
      tileX * TILE_SIZE,
      tileY * TILE_SIZE,
      TILE_SIZE,
      TILE_SIZE
    );
    this.playerDebugGraphics.lineStyle(2, color, 0.8);
    this.playerDebugGraphics.strokeRect(
      tileX * TILE_SIZE,
      tileY * TILE_SIZE,
      TILE_SIZE,
      TILE_SIZE
    );

    // 플레이어 중심점 표시 (발 위치)
    this.playerDebugGraphics.fillStyle(0xffffff, 1);
    this.playerDebugGraphics.fillCircle(pos.x, pos.y, 3);

    // 플레이어 충돌 박스 표시 (노란색)
    const collisionBox = this.playerController.getCollisionBox();
    this.playerDebugGraphics.lineStyle(2, 0xffff00, 0.9);
    this.playerDebugGraphics.strokeRect(
      collisionBox.x,
      collisionBox.y,
      collisionBox.width,
      collisionBox.height
    );

    // 디버그 텍스트 업데이트
    this.playerDebugText.setVisible(true);
    this.playerDebugText.setText([
      `Player Pos: (${pos.x.toFixed(0)}, ${pos.y.toFixed(0)})`,
      `Tile: (${tileX}, ${tileY})`,
      `Blocked: ${isBlocked ? 'YES' : 'NO'}`,
    ].join('\n'));
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
    const currentSlot = this.interactionSystem.getCurrentSlot();

    if (currentSlot === null) return;

    if (interaction === 'plant' && this.selectedSeed) {
      await this.plantCrop(currentSlot, this.selectedSeed);
    } else if (interaction === 'harvest') {
      const slotData = this.farmSlots.find(s => s.slot === currentSlot);
      if (!slotData?.cropCode) {
        this.farmData.onNotify('수확할 작물이 없습니다!', 'error');
        return;
      }
      if (slotData.stage < 6) {
        this.farmData.onNotify('아직 다 자라지 않았습니다!', 'error');
        return;
      }
      await this.harvestCrop(currentSlot);
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
   * farm_slots 데이터 업데이트 (React → Phaser)
   */
  updateFarmSlots(farmSize: number, farmSlots: FarmSlot[]): void {
    this.farmSize = farmSize;
    this.farmSlots = farmSlots;

    // 씬 초기화 전에 호출되면 무시
    if (!this.farmGridManager || !this.interactionSystem) {
      return;
    }

    // FarmGridManager 재렌더링
    this.farmGridManager.renderGrid(farmSize, farmSlots);

    // InteractionSystem 업데이트
    this.interactionSystem.updateFarmSlots(farmSlots);
  }

  /**
   * 배치 모드 업데이트 (React → Phaser)
   */
  updatePlacementMode(enabled: boolean, deleteMode: boolean): void {
    this.placementMode = enabled;
    this.deleteMode = deleteMode;

    if (!this.unifiedPlacementManager) return;

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
    if (!this.unifiedPlacementManager) return;

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
    if (!this.unifiedPlacementManager) return;
    this.unifiedPlacementManager.addItem(item);
  }

  /**
   * 아이템 제거
   */
  removePlacedItem(itemId: string): void {
    if (!this.unifiedPlacementManager) return;
    this.unifiedPlacementManager.removeItem(itemId);
  }

  /**
   * 배치 가능 여부 확인
   */
  canPlaceAt(tileX: number, tileY: number, width: number, height: number): boolean {
    if (!this.unifiedPlacementManager) return false;
    return this.unifiedPlacementManager.canPlaceAt(tileX, tileY, width, height);
  }

  /**
   * 아이템 로컬 배치 (API 호출 없음)
   */
  async placeItemLocally(itemCode: string, tileX: number, tileY: number, metadata: PlacedItem['metadata']): Promise<string | null> {
    if (!this.unifiedPlacementManager) return null;
    return this.unifiedPlacementManager.placeItemLocally(itemCode, tileX, tileY, metadata);
  }

  // ====== 배치 모드 저장/취소 메서드 ======

  /**
   * 배치 변경 사항이 있는지 확인
   */
  hasPlacementChanges(): boolean {
    if (!this.unifiedPlacementManager) return false;
    return this.unifiedPlacementManager.hasChanges();
  }

  /**
   * 배치 변경 사항 가져오기
   */
  getPlacementChanges() {
    if (!this.unifiedPlacementManager) return { moved: [], deleted: [], created: [] };
    return this.unifiedPlacementManager.getChanges();
  }

  /**
   * 배치 변경 사항 취소 (원래 상태로 복원)
   */
  revertPlacementChanges(): void {
    if (!this.unifiedPlacementManager) return;
    this.unifiedPlacementManager.revertChanges();
  }

  /**
   * 배치 변경 사항 확정 (저장 성공 후 호출)
   */
  confirmPlacementChanges(): void {
    if (!this.unifiedPlacementManager) return;
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
    this.farmGridManager?.destroy();

    // 디버그 그래픽스 정리
    if (this.playerDebugGraphics) {
      this.playerDebugGraphics.destroy();
      this.playerDebugGraphics = null;
    }
    if (this.playerDebugText) {
      this.playerDebugText.destroy();
      this.playerDebugText = null;
    }
  }
}
