/**
 * PlayerController - 플레이어 캐릭터 제어
 * 이동, 애니메이션, 경계 처리
 */

import Phaser from 'phaser';
import {
  MAP_WIDTH,
  MAP_HEIGHT,
  TILE_SIZE,
  PLAYER_SPEED,
  PLAYER_START_X,
  PLAYER_START_Y,
  ANIMATION_FRAME_RATE,
  HARVEST_FRAME_RATE,
} from '../config/gameConfig';
import { DEPTH, getEntityDepth } from '../config/depthConfig';

// 방향 상수
export type Direction = 'down' | 'up' | 'left' | 'right';

// 에셋 키
const ASSETS = {
  IDLE: 'farmer_idle',
  HARVEST: 'farmer_harvest',
  WATER: 'farmer_water',
};

// 에셋 경로
const ASSET_PATH = '/farm/characters/';

// 스프라이트시트 설정
// 실제 스프라이트시트 구조: 24열 x 3행 (캐릭터 높이 64px)
// - row 0: down (4프레임)
// - row 1: left/right
// - row 2: up
const SPRITE_CONFIG = {
  idle: {
    file: 'Farmer_1_32x32.png',
    frameWidth: 32,
    frameHeight: 64,        // 캐릭터 높이는 64px (2타일)
    columns: 24,            // 스프라이트시트 열 개수
    framesPerDirection: 4,  // 각 방향당 사용할 프레임 수
  },
  harvest: {
    file: 'Farmer_1_Harvesting_36_frames_32x32.png',
    frameWidth: 32,
    frameHeight: 64,        // 64px 높이
    columns: 36,            // 36열 × 1행 (모든 방향이 한 줄)
    framesPerDirection: 9,  // 9프레임 × 4방향 = 36프레임
  },
  water: {
    file: 'Farmer_1_Watering_56_frames_32x32.png',
    frameWidth: 32,
    frameHeight: 64,        // 64px 높이
    columns: 56,            // 56열 × 3행? (복잡한 구조)
    framesPerDirection: 14, // 14프레임 × 4방향 = 56프레임
  },
};

// 스프라이트시트 방향 순서 (row 0 idle, row 1 walk 모두 동일)
// 순서: right, up, left, down
const DIRECTION_INDEX: Record<Direction, number> = {
  right: 0,
  up: 1,
  left: 2,
  down: 3,
};

export class PlayerController {
  private scene: Phaser.Scene;
  private sprite!: Phaser.GameObjects.Sprite;
  private cursors: Phaser.Types.Input.Keyboard.CursorKeys | null = null;
  private wasd: { W: Phaser.Input.Keyboard.Key; A: Phaser.Input.Keyboard.Key; S: Phaser.Input.Keyboard.Key; D: Phaser.Input.Keyboard.Key } | null = null;
  private spaceKey: Phaser.Input.Keyboard.Key | null = null;

  private currentDirection: Direction = 'down';
  private isMoving: boolean = false;
  private isActionPlaying: boolean = false;

  // 액션 콜백
  private onActionCallback: (() => void) | null = null;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /**
   * 에셋 프리로드
   */
  preload(): void {
    // 기본 idle/walk
    this.scene.load.spritesheet(ASSETS.IDLE, ASSET_PATH + SPRITE_CONFIG.idle.file, {
      frameWidth: SPRITE_CONFIG.idle.frameWidth,
      frameHeight: SPRITE_CONFIG.idle.frameHeight,
    });

    // 수확 애니메이션
    this.scene.load.spritesheet(ASSETS.HARVEST, ASSET_PATH + SPRITE_CONFIG.harvest.file, {
      frameWidth: SPRITE_CONFIG.harvest.frameWidth,
      frameHeight: SPRITE_CONFIG.harvest.frameHeight,
    });

    // 물주기 애니메이션
    this.scene.load.spritesheet(ASSETS.WATER, ASSET_PATH + SPRITE_CONFIG.water.file, {
      frameWidth: SPRITE_CONFIG.water.frameWidth,
      frameHeight: SPRITE_CONFIG.water.frameHeight,
    });
  }

  /**
   * 플레이어 생성 및 초기화
   */
  create(): void {
    // 스프라이트 생성 (에셋 로드 완료 후)
    this.sprite = this.scene.add.sprite(PLAYER_START_X, PLAYER_START_Y, ASSETS.IDLE, 0);
    this.sprite.setOrigin(0.5, 1); // 발 위치 기준 (64px 높이)

    // 초기 depth 설정 (확실히 위에 보이도록)
    this.sprite.setDepth(150);
    this.updateDepth();

    // 입력 설정
    if (this.scene.input.keyboard) {
      this.cursors = this.scene.input.keyboard.createCursorKeys();
      this.wasd = {
        W: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W),
        A: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A),
        S: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S),
        D: this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D),
      };
      this.spaceKey = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
    }

    // 애니메이션 생성
    this.createAnimations();
  }

  /**
   * 애니메이션 정의
   * 스프라이트시트 구조 (Farmer_1_32x32.png):
   * - Row 0: 정적 멈춤 이미지 (4프레임, 사용 안함)
   * - Row 1: 숨쉬기 애니메이션 (6프레임 × 4방향 = 24프레임)
   * - Row 2: 걷기 애니메이션 (6프레임 × 4방향 = 24프레임)
   * 방향 순서: right, up, left, down
   */
  private createAnimations(): void {
    const directions: Direction[] = ['down', 'up', 'left', 'right'];
    const columns = SPRITE_CONFIG.idle.columns;  // 24
    const framesPerDir = 6;

    // Idle 애니메이션 (row 1 = 숨쉬기, 6프레임씩)
    directions.forEach((dir) => {
      const dirIndex = DIRECTION_INDEX[dir];
      // row 1 시작 (24) + 방향별 오프셋 (6프레임씩)
      const startFrame = columns + (dirIndex * framesPerDir);

      this.scene.anims.create({
        key: `idle_${dir}`,
        frames: this.scene.anims.generateFrameNumbers(ASSETS.IDLE, {
          start: startFrame,
          end: startFrame + framesPerDir - 1,
        }),
        frameRate: ANIMATION_FRAME_RATE / 2,  // 숨쉬기는 느리게
        repeat: -1,
      });
    });

    // Walk 애니메이션 (row 2 = 걷기, 6프레임씩)
    directions.forEach((dir) => {
      const dirIndex = DIRECTION_INDEX[dir];
      // row 2 시작 (48) + 방향별 오프셋 (6프레임씩)
      const startFrame = (columns * 2) + (dirIndex * framesPerDir);

      this.scene.anims.create({
        key: `walk_${dir}`,
        frames: this.scene.anims.generateFrameNumbers(ASSETS.IDLE, {
          start: startFrame,
          end: startFrame + framesPerDir - 1,
        }),
        frameRate: ANIMATION_FRAME_RATE,
        repeat: -1,
      });
    });

    // Harvest 애니메이션 (순차적 - 1행에 모든 방향)
    // 순서: down(0-8), left(9-17), right(18-26), up(27-35)
    const harvestFrames = SPRITE_CONFIG.harvest.framesPerDirection;
    const harvestOrder: Direction[] = ['down', 'left', 'right', 'up'];
    harvestOrder.forEach((dir, index) => {
      const startFrame = index * harvestFrames;
      this.scene.anims.create({
        key: `harvest_${dir}`,
        frames: this.scene.anims.generateFrameNumbers(ASSETS.HARVEST, {
          start: startFrame,
          end: startFrame + harvestFrames - 1,
        }),
        frameRate: HARVEST_FRAME_RATE,
        repeat: 0,
      });
    });

    // Water 애니메이션 (행 기반 - 3행 구조)
    const waterCols = SPRITE_CONFIG.water.columns;
    const waterFrames = SPRITE_CONFIG.water.framesPerDirection;
    const waterRowMap: Record<Direction, number> = { down: 0, left: 1, right: 1, up: 2 };
    directions.forEach((dir) => {
      const row = waterRowMap[dir];
      const startFrame = row * waterCols;
      this.scene.anims.create({
        key: `water_${dir}`,
        frames: this.scene.anims.generateFrameNumbers(ASSETS.WATER, {
          start: startFrame,
          end: startFrame + waterFrames - 1,
        }),
        frameRate: HARVEST_FRAME_RATE,
        repeat: 0,
      });
    });
  }

  /**
   * 매 프레임 업데이트
   */
  update(): void {
    if (this.isActionPlaying) return;

    this.handleMovement();
    this.handleActionInput();
    this.updateDepth();
  }

  /**
   * 이동 처리
   */
  private handleMovement(): void {
    let velocityX = 0;
    let velocityY = 0;

    // 방향 입력 확인
    const left = this.cursors?.left.isDown || this.wasd?.A.isDown;
    const right = this.cursors?.right.isDown || this.wasd?.D.isDown;
    const up = this.cursors?.up.isDown || this.wasd?.W.isDown;
    const down = this.cursors?.down.isDown || this.wasd?.S.isDown;

    if (left) {
      velocityX = -PLAYER_SPEED;
      this.currentDirection = 'left';
    } else if (right) {
      velocityX = PLAYER_SPEED;
      this.currentDirection = 'right';
    }

    if (up) {
      velocityY = -PLAYER_SPEED;
      if (!left && !right) this.currentDirection = 'up';
    } else if (down) {
      velocityY = PLAYER_SPEED;
      if (!left && !right) this.currentDirection = 'down';
    }

    // 대각선 이동 시 속도 정규화
    if (velocityX !== 0 && velocityY !== 0) {
      const factor = 1 / Math.sqrt(2);
      velocityX *= factor;
      velocityY *= factor;
    }

    // 이동 적용
    const deltaTime = this.scene.game.loop.delta / 1000;
    let newX = this.sprite.x + velocityX * deltaTime;
    let newY = this.sprite.y + velocityY * deltaTime;

    // 경계 제한 (맵 내부만)
    const margin = TILE_SIZE / 2;
    newX = Phaser.Math.Clamp(newX, margin, MAP_WIDTH - margin);
    newY = Phaser.Math.Clamp(newY, margin, MAP_HEIGHT - margin);

    this.sprite.setPosition(newX, newY);

    // 애니메이션 업데이트
    this.isMoving = velocityX !== 0 || velocityY !== 0;
    if (this.isMoving) {
      this.sprite.play(`walk_${this.currentDirection}`, true);
    } else {
      this.sprite.play(`idle_${this.currentDirection}`, true);
    }
  }

  /**
   * 액션 입력 처리 (SPACE)
   */
  private handleActionInput(): void {
    if (this.spaceKey && Phaser.Input.Keyboard.JustDown(this.spaceKey)) {
      if (this.onActionCallback) {
        this.onActionCallback();
      }
    }
  }

  /**
   * Y좌표 기반 깊이 업데이트
   */
  private updateDepth(): void {
    const depth = getEntityDepth(this.sprite.y, MAP_HEIGHT);
    this.sprite.setDepth(depth);
  }

  /**
   * 수확 애니메이션 재생
   */
  playHarvestAnimation(): Promise<void> {
    return this.playActionAnimation('harvest');
  }

  /**
   * 물주기 애니메이션 재생
   */
  playWaterAnimation(): Promise<void> {
    return this.playActionAnimation('water');
  }

  /**
   * 액션 애니메이션 재생 (공통)
   */
  private playActionAnimation(action: 'harvest' | 'water'): Promise<void> {
    return new Promise((resolve) => {
      this.isActionPlaying = true;
      const animKey = `${action}_${this.currentDirection}`;

      this.sprite.play(animKey);
      this.sprite.once('animationcomplete', () => {
        this.isActionPlaying = false;
        this.sprite.play(`idle_${this.currentDirection}`);
        resolve();
      });
    });
  }

  /**
   * 액션 콜백 설정 (SPACE 키 누를 때)
   */
  setActionCallback(callback: () => void): void {
    this.onActionCallback = callback;
  }

  /**
   * 플레이어 위치 가져오기
   */
  getPosition(): { x: number; y: number } {
    return { x: this.sprite.x, y: this.sprite.y };
  }

  /**
   * 현재 방향 가져오기
   */
  getDirection(): Direction {
    return this.currentDirection;
  }

  /**
   * 스프라이트 객체 가져오기
   */
  getSprite(): Phaser.GameObjects.Sprite {
    return this.sprite;
  }

  /**
   * 액션 중인지 확인
   */
  isPerformingAction(): boolean {
    return this.isActionPlaying;
  }

  /**
   * 정리
   */
  destroy(): void {
    this.sprite.destroy();
  }
}
