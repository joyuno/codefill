# Pixel Art Sprites 다운로드 가이드

이 폴더에 픽셀 아트 에셋을 다운로드하여 배치하세요.

## 추천 무료 에셋 (CC0/Free)

### 1. 작물 (Crops) - `/sprites/crops/`

**Farming Crops 16x16** (CC0)
- 다운로드: https://opengameart.org/content/farming-crops-16x16
- 내용: 20종 작물, 각 5단계 성장
- 크기: 16x16 픽셀
- 파일명: `crops.png`로 저장

포함 작물:
Turnip, Rose, Cucumber, Tulip, Tomato, Melon, Eggplant, Lemon,
Pineapple, Rice, Wheat, Grapes, Strawberry, Cassava, Potato,
Coffee, Orange, Avocado, Corn, Sunflower

### 2. 캐릭터 (Characters) - `/sprites/characters/`

**LPC Character Generator**
- 다운로드: https://opengameart.org/content/lpc-collection
- 또는: https://sanderfrenken.github.io/Universal-LPC-Spritesheet-Character-Generator/
- 크기: 64x64 픽셀 (프레임당)
- 파일명: `farmer.png`로 저장

**Sprout Lands Character** (무료 버전)
- 다운로드: https://cupnooble.itch.io/sprout-lands-asset-pack
- 크기: 48x48 또는 32x32 픽셀

### 3. 건물 (Buildings) - `/sprites/buildings/`

**LPC Farming Buildings**
- 다운로드: https://opengameart.org/content/lpc-farming
- 내용: 농장 건물, 헛간, 닭장 등
- 파일명: `houses.png`, `farm.png`로 저장

### 4. 타일 (Tiles) - `/sprites/tiles/`

**LPC Terrain**
- 다운로드: https://opengameart.org/content/lpc-terrain-repack
- 내용: 잔디, 흙, 물, 길 타일
- 파일명: `terrain.png`로 저장

### 5. UI 요소 - `/sprites/ui/`

**Free Pixel Art RPG UI**
- 다운로드: https://itch.io/game-assets/free/tag-pixel-art/tag-user-interface
- 내용: 버튼, 프레임, 아이콘

---

## 폴더 구조

```
/public/sprites/
├── crops/
│   └── crops.png          # 20종 작물 x 5단계 = 100 프레임
├── characters/
│   └── farmer.png         # 캐릭터 스프라이트 시트
├── buildings/
│   ├── houses.png         # 집 업그레이드 단계
│   └── farm.png           # 농장 건물
├── tiles/
│   └── terrain.png        # 지형 타일
└── ui/
    ├── buttons.png        # 버튼
    └── frames.png         # UI 프레임
```

## 라이센스

- CC0: 제한 없이 자유롭게 사용 가능
- CC-BY: 저작자 표기 필요
- CC-BY-SA: 저작자 표기 + 동일 조건 공유

사용하는 에셋의 라이센스를 확인하고, 필요시 크레딧을 표기하세요.

## 스프라이트 시트 사용법

```tsx
import { Sprite, CropSprite } from '@/components/farm/SpriteSheet';

// 기본 스프라이트
<Sprite
  src="/sprites/crops/crops.png"
  frameWidth={16}
  frameHeight={16}
  frame={2}      // 3번째 프레임 (0부터 시작)
  row={0}        // 첫 번째 행
  scale={3}      // 3배 확대
/>

// 작물 스프라이트 (편의 컴포넌트)
<CropSprite crop="tomato" stage={4} scale={3} />
```
