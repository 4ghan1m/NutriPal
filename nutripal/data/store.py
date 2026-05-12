"""JSON file-based data persistence."""
import json
from pathlib import Path
from typing import Optional
from .models import Profile, Fridge, FridgeItem, MealPlan


class DataStore:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._profile_path = self.data_dir / "profile.json"
        self._fridge_path = self.data_dir / "fridge.json"
        self._history_path = self.data_dir / "history.json"

    def _read_json(self, path: Path, default: dict) -> dict:
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default

    def _write_json(self, path: Path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---- Profile ----

    def get_profile(self) -> Optional[Profile]:
        data = self._read_json(self._profile_path, {})
        if not data:
            return None
        return Profile(**data)

    def save_profile(self, profile: Profile) -> None:
        self._write_json(self._profile_path, profile.model_dump())

    def is_onboarding_complete(self) -> bool:
        profile = self.get_profile()
        return profile is not None and profile.onboarding_complete

    # ---- Fridge ----

    def get_fridge(self) -> Fridge:
        data = self._read_json(self._fridge_path, {"items": []})
        return Fridge(**data)

    def save_fridge(self, fridge: Fridge) -> None:
        self._write_json(self._fridge_path, fridge.model_dump())

    def add_fridge_item(self, name: str, quantity: float, unit: str) -> Fridge:
        fridge = self.get_fridge()
        for item in fridge.items:
            if item.name == name and item.unit == unit:
                item.quantity += quantity
                self.save_fridge(fridge)
                return fridge
        fridge.items.append(FridgeItem(name=name, quantity=quantity, unit=unit))
        self.save_fridge(fridge)
        return fridge

    def remove_fridge_item(self, name: str) -> Fridge:
        fridge = self.get_fridge()
        fridge.items = [i for i in fridge.items if i.name != name]
        self.save_fridge(fridge)
        return fridge

    def clear_fridge(self) -> Fridge:
        fridge = Fridge(items=[])
        self.save_fridge(fridge)
        return fridge

    # ---- History ----

    def get_history(self, limit: int = 10) -> list[MealPlan]:
        data = self._read_json(self._history_path, {"plans": []})
        plans = [MealPlan(**p) for p in data.get("plans", [])]
        return plans[-limit:]

    def add_plan(self, plan: MealPlan) -> None:
        data = self._read_json(self._history_path, {"plans": []})
        data["plans"].append(plan.model_dump())
        self._write_json(self._history_path, data)
