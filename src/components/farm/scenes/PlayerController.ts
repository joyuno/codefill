/**
 * PlayerController - 플레이어 캐릭터 제어
 * 레이어 기반 캐릭터 합성 시스템
 * 이동, 애니메이션, 경계 처리
 */

import * as Phaser from 'phaser';
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
import { getEntityDepth } from '../config/depthConfig';
import type { CharacterData } from '@/lib/api/farm';

// 방향 상수
export type Direction = 'down' | 'up' | 'left' | 'right';

// 레이어 타입
type LayerType = 'body' | 'eyes' | 'outfit' | 'hair' | 'accessory';

// 레이어 기반 에셋 경로
const PARTS_PATH = '/farm/characters/parts/';

// Fallback 에셋 (액션 애니메이션용 - 프리컴포즈드)
const FALLBACK_ASSETS = {
  HARVEST: 'farmer_harvest',
  WATER: 'farmer_water',
};

const FALLBACK_PATH = '/farm/characters/';

// 레이어 기반 스프라이트시트 설정 (1792x704, 56열 x 11행)
const LAYER_SPRITE_CONFIG = {
  frameWidth: 32,
  frameHeight: 64,
  columns: 56,         // 1792 / 32 = 56
  rows: 11,            // 704 / 64 = 11
  framesPerDirection: 6,
};

// 스프라이트시트 행 구조
const ROW_MAP = {
  static: 0,    // 정적 이미지
  idle: 1,      // 숨쉬기 (6프레임 x 4방향)
  walk: 2,      // 걷기 (6프레임 x 4방향)
  harvest: 3,   // 수확
  dig: 4,       // 땅파기
  water: 5,     // 물주기
  chop: 6,      // 나무베기
  // 7-10: 낚시
};

// 방향 인덱스 (스프라이트시트 내 순서: right, up, left, down)
const DIRECTION_INDEX: Record<Direction, number> = {
  right: 0,
  up: 1,
  left: 2,
  down: 3,
};

// 기본 캐릭터 데이터 (fallback)
const DEFAULT_CHARACTER: CharacterData = {
  name: '농부',
  body: 'Body_1',
  hair: 'Short_Brown_Dark',
  hairColor: '#3d2314',
  face: 'Eyes_Brown',
  outfit: 'Outfit_Dungarees_Green',
  outfitColor: '#27ae60',
  accessory: 'none',
  farmName: '나의 농장',
};

export class PlayerController {
  private scene: Phaser.Scene;
  private characterData: CharacterData;

  // 레이어 기반 렌더링
  private container!: Phaser.GameObjects.Container;
  private layers: Map<LayerType, Phaser.GameObjects.Sprite> = new Map();

  // Fallback 스프라이트 (액션 애니메이션용)
  private fallbackSprite!: Phaser.GameObjects.Sprite;
  private useFallbackForAction: boolean = false;

  // 입력
  private cursors: Phaser.Types.Input.Keyboard.CursorKeys | null = null;
  private wasd: { W: Phaser.Input.Keyboard.Key; A: Phaser.Input.Keyboard.Key; S: Phaser.Input.Keyboard.Key; D: Phaser.Input.Keyboard.Key } | null = null;
  private spaceKey: Phaser.Input.Keyboard.Key | null = null;

  private currentDirection: Direction = 'down';
  private isMoving: boolean = false;
  private isActionPlaying: boolean = false;

  // 액션 콜백
  private onActionCallback: (() => void) | null = null;

  constructor(scene: Phaser.Scene, characterData?: CharacterData | null) {
    this.scene = scene;
    this.characterData = characterData || DEFAULT_CHARACTER;
  }

  /**
   * 캐릭터 데이터 업데이트
   */
  updateCharacterData(characterData: CharacterData): void {
    this.characterData = characterData;
    // 런타임 중 캐릭터 변경이 필요하면 레이어 재로드 로직 추가
  }

  /**
   * 에셋 프리로드 - 레이어별 스프라이트시트
   */
  preload(): void {
    const char = this.characterData;

    // Body 레이어
    const bodyKey = `layer_body_${char.body}`;
    if (!this.scene.textures.exists(bodyKey)) {
      this.scene.load.spritesheet(bodyKey, `${PARTS_PATH}bodies/${char.body}.png`, {
        frameWidth: LAYER_SPRITE_CONFIG.frameWidth,
        frameHeight: LAYER_SPRITE_CONFIG.frameHeight,
      });
    }

    // Eyes 레이어
    const eyesKey = `layer_eyes_${char.face}`;
    if (!this.scene.textures.exists(eyesKey)) {
      this.scene.load.spritesheet(eyesKey, `${PARTS_PATH}eyes/${char.face}.png`, {
        frameWidth: LAYER_SPRITE_CONFIG.frameWidth,
        frameHeight: LAYER_SPRITE_CONFIG.frameHeight,
      });
    }

    // Outfit 레이어
    const outfitKey = `layer_outfit_${char.outfit}`;
    if (!this.scene.textures.exists(outfitKey)) {
      this.scene.load.spritesheet(outfitKey, `${PARTS_PATH}outfits/${char.outfit}.png`, {
        frameWidth: LAYER_SPRITE_CONFIG.frameWidth,
        frameHeight: LAYER_SPRITE_CONFIG.frameHeight,
      });
    }

    // Hair 레이어 (Hairstyle_Short_Brown_Dark 형태)
    const hairKey = `layer_hair_${char.hair}`;
    if (!this.scene.textures.exists(hairKey)) {
      this.scene.load.spritesheet(hairKey, `${PARTS_PATH}hairstyles/Hairstyle_${char.hair}.png`, {
        frameWidth: LAYER_SPRITE_CONFIG.frameWidth,
        frameHeight: LAYER_SPRITE_CONFIG.frameHeight,
      });
    }

    // Accessory 레이어 (optional)
    if (char.accessory && char.accessory !== 'none') {
      const accKey = `layer_accessory_${char.accessory}`;
      if (!this.scene.textures.exists(accKey)) {
        this.scene.load.spritesheet(accKey, `${PARTS_PATH}accessories/${char.accessory}.png`, {
          frameWidth: LAYER_SPRITE_CONFIG.frameWidth,
          frameHeight: LAYER_SPRITE_CONFIG.frameHeight,
        });
      }
    }

    // Fallback 에셋 (액션 애니메이션용 - 프리컴포즈드)
    if (!this.scene.textures.exists(FALLBACK_ASSETS.HARVEST)) {
      this.scene.load.spritesheet(FALLBACK_ASSETS.HARVEST, `${FALLBACK_PATH}Farmer_1_Harvesting_36_frames_32x32.png`, {
        frameWidth: 32,
        frameHeight: 64,
      });
    }
    if (!this.scene.textures.exists(FALLBACK_ASSETS.WATER)) {
      this.scene.load.spritesheet(FALLBACK_ASSETS.WATER, `${FALLBACK_PATH}Farmer_1_Watering_56_frames_32x32.png`, {
        frameWidth: 32,
        frameHeight: 64,
      });
    }
  }

  /**
   * 플레이어 생성 및 초기화
   */
  create(): void {
    const char = this.characterData;

    // 컨테이너 생성
    this.container = this.scene.add.container(PLAYER_START_X, PLAYER_START_Y);

    // 레이어 순서대로 스프라이트 생성 및 추가 (아래→위)
    const layerOrder: { type: LayerType; key: string }[] = [
      { type: 'body', key: `layer_body_${char.body}` },
      { type: 'eyes', key: `layer_eyes_${char.face}` },
      { type: 'outfit', key: `layer_outfit_${char.outfit}` },
      { type: 'hair', key: `layer_hair_${char.hair}` },
    ];

    // Accessory (optional)
    if (char.accessory && char.accessory !== 'none') {
      layerOrder.push({ type: 'accessory', key: `layer_accessory_${char.accessory}` });
    }

    layerOrder.forEach(({ type, key }) => {
      if (this.scene.textures.exists(key)) {
        const sprite = this.scene.add.sprite(0, 0, key, 0);
        sprite.setOrigin(0.5, 1); // 발 위치 기준
        this.layers.set(type, sprite);
        this.container.add(sprite);
      }
    });

    // Fallback 스프라이트 (액션용, 숨김 상태로 생성)
    this.fallbackSprite = this.scene.add.sprite(0, 0, FALLBACK_ASSETS.HARVEST, 0);
    this.fallbackSprite.setOrigin(0.5, 1);
    this.fallbackSprite.setVisible(false);
    this.container.add(this.fallbackSprite);

    // 초기 depth 설정
    this.container.setDepth(150);
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
    this.createLayerAnimations();
    this.createFallbackAnimations();

    // 초기 애니메이션 재생
    this.playLayerAnimation('idle', this.currentDirection);
  }

  /**
   * 레이어 기반 애니메이션 생성
   */
  private createLayerAnimations(): void {
    const directions: Direction[] = ['down', 'up', 'left', 'right'];
    const { columns, framesPerDirection } = LAYER_SPRITE_CONFIG;

    this.layers.forEach((sprite, layerType) => {
      const textureKey = sprite.texture.key;

      // Idle 애니메이션 (row 1)
      directions.forEach((dir) => {
        const dirIndex = DIRECTION_INDEX[dir];
        const startFrame = (ROW_MAP.idle * columns) + (dirIndex * framesPerDirection);
        const animKey = `${textureKey}_idle_${dir}`;

        if (!this.scene.anims.exists(animKey)) {
          this.scene.anims.create({
            key: animKey,
            frames: this.scene.anims.generateFrameNumbers(textureKey, {
              start: startFrame,
              end: startFrame + framesPerDirection - 1,
            }),
            frameRate: ANIMATION_FRAME_RATE / 2,
            repeat: -1,
          });
        }
      });

      // Walk 애니메이션 (row 2)
      directions.forEach((dir) => {
        const dirIndex = DIRECTION_INDEX[dir];
        const startFrame = (ROW_MAP.walk * columns) + (dirIndex * framesPerDirection);
        const animKey = `${textureKey}_walk_${dir}`;

        if (!this.scene.anims.exists(animKey)) {
          this.scene.anims.create({
            key: animKey,
            frames: this.scene.anims.generateFrameNumbers(textureKey, {
              start: startFrame,
              end: startFrame + framesPerDirection - 1,
            }),
            frameRate: ANIMATION_FRAME_RATE,
            repeat: -1,
          });
        }
      });

      // Harvest 애니메이션 (row 3) - 레이어 기반
      directions.forEach((dir) => {
        const dirIndex = DIRECTION_INDEX[dir];
        const startFrame = (ROW_MAP.harvest * columns) + (dirIndex * framesPerDirection);
        const animKey = `${textureKey}_harvest_${dir}`;

        if (!this.scene.anims.exists(animKey)) {
          this.scene.anims.create({
            key: animKey,
            frames: this.scene.anims.generateFrameNumbers(textureKey, {
              start: startFrame,
              end: startFrame + framesPerDirection - 1,
            }),
            frameRate: HARVEST_FRAME_RATE,
            repeat: 0,
          });
        }
      });

      // Water 애니메이션 (row 5) - 레이어 기반
      directions.forEach((dir) => {
        const dirIndex = DIRECTION_INDEX[dir];
        const startFrame = (ROW_MAP.water * columns) + (dirIndex * framesPerDirection);
        const animKey = `${textureKey}_water_${dir}`;

        if (!this.scene.anims.exists(animKey)) {
          this.scene.anims.create({
            key: animKey,
            frames: this.scene.anims.generateFrameNumbers(textureKey, {
              start: startFrame,
              end: startFrame + framesPerDirection - 1,
            }),
            frameRate: HARVEST_FRAME_RATE,
            repeat: 0,
          });
        }
      });
    });
  }

  /**
   * Fallback 애니메이션 생성 (프리컴포즈드 스프라이트용)
   */
  private createFallbackAnimations(): void {
    const directions: Direction[] = ['down', 'up', 'left', 'right'];

    // Harvest (순차적 - 1행에 모든 방향)
    const harvestFrames = 9;
    const harvestOrder: Direction[] = ['down', 'left', 'right', 'up'];
    harvestOrder.forEach((dir, index) => {
      const startFrame = index * harvestFrames;
      const animKey = `fallback_harvest_${dir}`;
      if (!this.scene.anims.exists(animKey)) {
        this.scene.anims.create({
          key: animKey,
          frames: this.scene.anims.generateFrameNumbers(FALLBACK_ASSETS.HARVEST, {
            start: startFrame,
            end: startFrame + harvestFrames - 1,
          }),
          frameRate: HARVEST_FRAME_RATE,
          repeat: 0,
        });
      }
    });

    // Water (행 기반)
    const waterFrames = 14;
    const waterRowMap: Record<Direction, number> = { down: 0, left: 1, right: 1, up: 2 };
    directions.forEach((dir) => {
      const row = waterRowMap[dir];
      const startFrame = row * 56; // 56열
      const animKey = `fallback_water_${dir}`;
      if (!this.scene.anims.exists(animKey)) {
        this.scene.anims.create({
          key: animKey,
          frames: this.scene.anims.generateFrameNumbers(FALLBACK_ASSETS.WATER, {
            start: startFrame,
            end: startFrame + waterFrames - 1,
          }),
          frameRate: HARVEST_FRAME_RATE,
          repeat: 0,
        });
      }
    });
  }

  /**
   * 모든 레이어에 동시에 애니메이션 재생
   */
  private playLayerAnimation(action: 'idle' | 'walk' | 'harvest' | 'water', direction: Direction): void {
    this.layers.forEach((sprite) => {
      const textureKey = sprite.texture.key;
      const animKey = `${textureKey}_${action}_${direction}`;
      if (this.scene.anims.exists(animKey)) {
        sprite.play(animKey, true);
      }
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
    let newX = this.container.x + velocityX * deltaTime;
    let newY = this.container.y + velocityY * deltaTime;

    // 경계 제한 (맵 내부만)
    const margin = TILE_SIZE / 2;
    newX = Phaser.Math.Clamp(newX, margin, MAP_WIDTH - margin);
    newY = Phaser.Math.Clamp(newY, margin, MAP_HEIGHT - margin);

    this.container.setPosition(newX, newY);

    // 애니메이션 업데이트
    const wasMoving = this.isMoving;
    this.isMoving = velocityX !== 0 || velocityY !== 0;

    if (this.isMoving) {
      this.playLayerAnimation('walk', this.currentDirection);
    } else if (wasMoving || !this.isMoving) {
      this.playLayerAnimation('idle', this.currentDirection);
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
    const depth = getEntityDepth(this.container.y, MAP_HEIGHT);
    this.container.setDepth(depth);
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
   * 액션 애니메이션 재생 (레이어 기반 또는 fallback)
   */
  private playActionAnimation(action: 'harvest' | 'water'): Promise<void> {
    return new Promise((resolve) => {
      this.isActionPlaying = true;

      // 레이어 기반 애니메이션 사용
      this.playLayerAnimation(action, this.currentDirection);

      // 첫 번째 레이어의 애니메이션 완료 이벤트 리스닝
      const firstLayer = this.layers.values().next().value;
      if (firstLayer) {
        firstLayer.once('animationcomplete', () => {
          this.isActionPlaying = false;
          this.playLayerAnimation('idle', this.currentDirection);
          resolve();
        });
      } else {
        // 레이어가 없으면 fallback
        this.playFallbackActionAnimation(action).then(resolve);
      }
    });
  }

  /**
   * Fallback 액션 애니메이션 재생
   */
  private playFallbackActionAnimation(action: 'harvest' | 'water'): Promise<void> {
    return new Promise((resolve) => {
      // 레이어 숨기기
      this.layers.forEach((sprite) => sprite.setVisible(false));

      // Fallback 스프라이트 보이기
      this.fallbackSprite.setVisible(true);
      this.fallbackSprite.setTexture(action === 'harvest' ? FALLBACK_ASSETS.HARVEST : FALLBACK_ASSETS.WATER);

      const animKey = `fallback_${action}_${this.currentDirection}`;
      this.fallbackSprite.play(animKey);

      this.fallbackSprite.once('animationcomplete', () => {
        // Fallback 숨기기
        this.fallbackSprite.setVisible(false);

        // 레이어 다시 보이기
        this.layers.forEach((sprite) => sprite.setVisible(true));

        this.isActionPlaying = false;
        this.playLayerAnimation('idle', this.currentDirection);
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
    return { x: this.container.x, y: this.container.y };
  }

  /**
   * 현재 방향 가져오기
   */
  getDirection(): Direction {
    return this.currentDirection;
  }

  /**
   * 컨테이너 객체 가져오기
   */
  getSprite(): Phaser.GameObjects.Container {
    return this.container;
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
    this.layers.forEach((sprite) => sprite.destroy());
    this.layers.clear();
    this.fallbackSprite.destroy();
    this.container.destroy();
  }
}
