from typing import List, Optional

from repositories.inventory_repository import InventoryRepository


class InventoryService:
    @staticmethod
    async def get_user_inventory(user_id: str) -> List[dict]:
        items = await InventoryRepository.find_by_user(user_id)
        return [
            {
                "id": str(i["_id"]),
                "name": i["name"],
                "type": i["type"],
                "rarity": i["rarity"],
                "count": i.get("count", 1),
                "rank": i.get("rank"),
                "polarity": i.get("polarity", []),
                "extra": i.get("extra", {}),
            }
            for i in items
        ]

    @staticmethod
    async def get_inventory_item(item_id: str, user_id: str) -> Optional[dict]:
        item = await InventoryRepository.find_by_id_and_user(item_id, user_id)
        if not item:
            return None
        return {
            "id": str(item["_id"]),
            "name": item["name"],
            "type": item["type"],
            "rarity": item["rarity"],
            "count": item.get("count", 1),
            "rank": item.get("rank"),
            "polarity": item.get("polarity", []),
            "extra": item.get("extra", {}),
        }
