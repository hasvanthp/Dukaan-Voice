import re
from dataclasses import dataclass


@dataclass
class IntentResult:
    intent: str
    entities: dict
    confidence: float


class RuleBasedIntentService:
    quantity_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(kilo|kg|litre|liter|pcs|piece|packet)?", re.IGNORECASE)

    def detect(self, text: str) -> IntentResult:
        lower = text.lower()
        if "udhaar" in lower or "credit" in lower:
            return IntentResult("record_payment", self._extract_amount_or_qty(lower), 0.72)
        if "sales" in lower or "sale" in lower:
            return IntentResult("check_sales", {}, 0.78)
        if "profit" in lower:
            return IntentResult("check_profit", {}, 0.78)
        if "stock" in lower or "inventory" in lower or "add" in lower:
            entities = self._extract_inventory_entities(text)
            return IntentResult("add_inventory", entities, entities.get("confidence", 0.65))
        return IntentResult("unknown", {}, 0.32)

    def _extract_amount_or_qty(self, text: str) -> dict:
        numbers = self.quantity_pattern.findall(text)
        quantity = float(numbers[-1][0]) if numbers else None
        return {"amount": quantity}

    def _extract_inventory_entities(self, text: str) -> dict:
        lower = text.lower()
        split_markers = ["nahi", "nahin", "no", "instead"]
        latest_segment = lower
        for marker in split_markers:
            if marker in lower:
                latest_segment = lower.split(marker)[-1]
        qty_matches = self.quantity_pattern.findall(latest_segment)
        qty = float(qty_matches[-1][0]) if qty_matches else None

        words = [w.strip(".,?!") for w in latest_segment.split() if w.isalpha()]
        skip_words = {"kilo", "kg", "stock", "mein", "add", "karo", "ka", "ki", "ko", "hai", "bacha", "kitna", "aaj", "kal", "nahi", "nahin"}
        product = next((w for w in words if w not in skip_words), None)

        confidence = 0.85 if qty and product else 0.6 if qty else 0.4
        return {"product_name": product, "quantity": qty, "unit": "kg", "confidence": confidence}
