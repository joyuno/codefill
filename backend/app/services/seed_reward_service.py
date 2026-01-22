"""
Seed Reward Service - 문제 풀이 시 씨앗 보상 시스템

- 첫 정답 시에만 씨앗 1개 지급 (재풀이 X)
- 난이도별 확률 기반 등급 결정
- Epic 씨앗은 챌린지/미션에서만 획득 가능
"""

import random
from typing import Optional, Dict, Any


# 작물 목록 (등급별)
CROPS_BY_RARITY = {
    "common": ["carrot", "radish", "turnip", "onion", "tomato", "grain"],
    "uncommon": ["cauliflower", "corn", "chili_pepper", "strawberry", "zucchini", "cotton"],
    "rare": ["pumpkin", "grape", "coffee", "prickly_pear"],
    # Epic은 문제풀이에서 제외 (챌린지/미션 전용)
    # "epic": ["watermelon", "pineapple"],
}

# 난이도별 등급 확률 가중치
DIFFICULTY_RARITY_WEIGHTS = {
    "easy": {"common": 1.0, "uncommon": 0.0, "rare": 0.0},
    "medium": {"common": 0.7, "uncommon": 0.3, "rare": 0.0},
    "medium_hard": {"common": 0.4, "uncommon": 0.6, "rare": 0.0},
    "hard": {"common": 0.2, "uncommon": 0.7, "rare": 0.1},
    "very_hard": {"common": 0.1, "uncommon": 0.6, "rare": 0.3},
}

# 작물 한국어 이름 매핑
CROP_NAMES_KO = {
    # Common
    "carrot": "당근",
    "radish": "무",
    "turnip": "순무",
    "onion": "양파",
    "tomato": "토마토",
    "grain": "밀",
    # Uncommon
    "cauliflower": "콜리플라워",
    "corn": "옥수수",
    "chili_pepper": "고추",
    "strawberry": "딸기",
    "zucchini": "호박",
    "cotton": "목화",
    # Rare
    "pumpkin": "호박",
    "grape": "포도",
    "coffee": "커피",
    "prickly_pear": "선인장 열매",
    # Epic (챌린지/미션용)
    "watermelon": "수박",
    "pineapple": "파인애플",
}


class SeedRewardService:
    """씨앗 보상 서비스"""

    def select_rarity(self, difficulty: str) -> str:
        """
        난이도에 따라 확률적으로 등급(rarity) 선택

        Args:
            difficulty: 문제 난이도 (easy, medium, medium_hard, hard, very_hard)

        Returns:
            선택된 등급 (common, uncommon, rare)
        """
        weights = DIFFICULTY_RARITY_WEIGHTS.get(difficulty, DIFFICULTY_RARITY_WEIGHTS["medium"])

        # 가중치 기반 랜덤 선택
        rarities = list(weights.keys())
        probabilities = list(weights.values())

        chosen_rarity = random.choices(rarities, weights=probabilities, k=1)[0]
        return chosen_rarity

    def select_seed(self, rarity: str) -> str:
        """
        등급 내에서 랜덤하게 작물 선택

        Args:
            rarity: 등급 (common, uncommon, rare)

        Returns:
            선택된 작물 코드 (예: "carrot")
        """
        crops = CROPS_BY_RARITY.get(rarity, CROPS_BY_RARITY["common"])
        return random.choice(crops)

    def award_seed(
        self,
        user_id: str,
        difficulty: str,
        db
    ) -> Optional[Dict[str, Any]]:
        """
        사용자에게 씨앗 보상 지급

        Args:
            user_id: 사용자 UUID
            difficulty: 문제 난이도
            db: Supabase 클라이언트

        Returns:
            지급된 씨앗 정보 딕셔너리 또는 None
            {
                "seed_code": "seed_carrot",
                "crop_code": "carrot",
                "rarity": "common",
                "crop_name_ko": "당근"
            }
        """
        try:
            # 1. 등급 결정
            rarity = self.select_rarity(difficulty)

            # 2. 작물 선택
            crop_code = self.select_seed(rarity)

            # 3. 씨앗 코드 생성
            seed_code = f"seed_{crop_code}"

            # 4. 한국어 이름 가져오기
            crop_name_ko = CROP_NAMES_KO.get(crop_code, crop_code)

            # 5. 인벤토리에 씨앗 추가
            self._add_to_inventory(db, user_id, seed_code, 1)

            print(f"[SeedReward] Awarded {seed_code} ({rarity}) to user {user_id}")

            return {
                "seed_code": seed_code,
                "crop_code": crop_code,
                "rarity": rarity,
                "crop_name_ko": crop_name_ko
            }

        except Exception as e:
            print(f"[SeedReward] Error awarding seed: {e}")
            return None

    def _add_to_inventory(self, db, user_id: str, item_code: str, quantity: int = 1) -> None:
        """
        인벤토리에 아이템 추가 (farm_service.update_inventory 참고)

        Args:
            db: Supabase 클라이언트
            user_id: 사용자 UUID
            item_code: 아이템 코드
            quantity: 추가할 수량
        """
        # 기존 아이템 확인
        existing = db.table("user_inventory")\
            .select("quantity")\
            .eq("user_id", user_id)\
            .eq("item_code", item_code)\
            .execute()

        if existing.data and len(existing.data) > 0:
            # 기존 수량에 추가
            new_quantity = existing.data[0]["quantity"] + quantity
            db.table("user_inventory").update({"quantity": new_quantity})\
                .eq("user_id", user_id)\
                .eq("item_code", item_code)\
                .execute()
        else:
            # 새 아이템 추가
            db.table("user_inventory").insert({
                "user_id": user_id,
                "item_code": item_code,
                "quantity": quantity,
            }).execute()


# 싱글톤 인스턴스
_seed_reward_service: Optional[SeedRewardService] = None


def get_seed_reward_service() -> SeedRewardService:
    """SeedRewardService 싱글톤 인스턴스 반환"""
    global _seed_reward_service
    if _seed_reward_service is None:
        _seed_reward_service = SeedRewardService()
    return _seed_reward_service
