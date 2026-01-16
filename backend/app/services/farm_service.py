"""
Farm Service - 농장/상점 공통 헬퍼 함수

shop.py, placement.py에서 중복되던 함수들을 통합
"""

from fastapi import HTTPException, status
from uuid import UUID
import json
from typing import Optional, Dict, Any, List

from ..models.placement import ItemMetadata


class FarmService:
    """농장/상점 관련 공통 서비스"""

    @staticmethod
    def get_user_farm(db, user_id: UUID) -> dict:
        """사용자 농장 조회"""
        result = db.table("user_farm")\
            .select("id, user_id, gold, farm_level, farm_size, farm_slots")\
            .eq("user_id", str(user_id))\
            .execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="농장을 찾을 수 없습니다. 캐릭터를 먼저 생성해주세요."
        )

    @staticmethod
    def get_user_inventory(db, user_id: UUID) -> Dict[str, int]:
        """사용자 인벤토리 조회 (딕셔너리 형태: {item_code: quantity})"""
        result = db.table("user_inventory")\
            .select("item_code, quantity")\
            .eq("user_id", str(user_id))\
            .execute()
        return {item["item_code"]: item["quantity"] for item in (result.data or [])}

    @staticmethod
    def update_inventory(db, user_id: UUID, item_code: str, quantity_change: int) -> None:
        """인벤토리 수량 업데이트"""
        existing = db.table("user_inventory")\
            .select("quantity")\
            .eq("user_id", str(user_id))\
            .eq("item_code", item_code)\
            .execute()

        if existing.data and len(existing.data) > 0:
            new_quantity = existing.data[0]["quantity"] + quantity_change
            if new_quantity <= 0:
                db.table("user_inventory").delete()\
                    .eq("user_id", str(user_id))\
                    .eq("item_code", item_code)\
                    .execute()
            else:
                db.table("user_inventory").update({"quantity": new_quantity})\
                    .eq("user_id", str(user_id))\
                    .eq("item_code", item_code)\
                    .execute()
        elif quantity_change > 0:
            db.table("user_inventory").insert({
                "user_id": str(user_id),
                "item_code": item_code,
                "quantity": quantity_change,
            }).execute()

    @staticmethod
    def parse_metadata(metadata_json: Any) -> ItemMetadata:
        """메타데이터 JSON을 ItemMetadata로 변환"""
        if isinstance(metadata_json, str):
            metadata_json = json.loads(metadata_json) if metadata_json else {}
        if not metadata_json:
            metadata_json = {}

        return ItemMetadata(
            sprite=metadata_json.get("sprite", "default"),
            width=metadata_json.get("width", 1),
            height=metadata_json.get("height", 1),
            depth=metadata_json.get("depth", 50),
            canMove=metadata_json.get("canMove", True),
            canDelete=metadata_json.get("canDelete", True),
            anchor=metadata_json.get("anchor"),
            collision=metadata_json.get("collision"),
        )

    @staticmethod
    def get_shop_items_metadata(db, item_codes: List[str]) -> Dict[str, ItemMetadata]:
        """
        여러 상점 아이템의 메타데이터를 배치 조회 (N+1 방지)

        Args:
            db: 데이터베이스 연결
            item_codes: 아이템 코드 목록

        Returns:
            {item_code: ItemMetadata} 딕셔너리
        """
        if not item_codes:
            return {}

        result = db.table("shop_items")\
            .select("code, metadata")\
            .in_("code", item_codes)\
            .execute()

        return {
            item["code"]: FarmService.parse_metadata(item.get("metadata", {}))
            for item in (result.data or [])
        }

    @staticmethod
    def get_shop_item(db, item_code: str) -> dict:
        """상점 아이템 정보 조회"""
        result = db.table("shop_items")\
            .select("code, name, name_ko, category, rarity, price, max_quantity, metadata")\
            .eq("code", item_code)\
            .execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 아이템입니다"
            )
        return result.data[0]
