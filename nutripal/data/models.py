"""Pydantic models for NutriPal data structures."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class Goal(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    GAIN_MUSCLE = "gain_muscle"
    MAINTAIN = "maintain"
    CUSTOM = "custom"


class Profile(BaseModel):
    height_cm: float = Field(ge=100, le=250, description="Height in cm")
    weight_kg: float = Field(ge=20, le=300, description="Weight in kg")
    age: int = Field(ge=1, le=120, description="Age in years")
    gender: Gender = Gender.OTHER
    activity_level: ActivityLevel = ActivityLevel.MODERATE
    goal: Goal = Goal.MAINTAIN
    onboarding_complete: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def bmr(self) -> float:
        """Mifflin-St Jeor equation for BMR estimation."""
        if self.gender == Gender.MALE:
            return 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            return 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

    def daily_calories(self) -> int:
        """TDEE estimate based on activity level."""
        multiplier = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9,
        }
        return int(self.bmr() * multiplier[self.activity_level])

    def target_calories(self) -> int:
        """Daily calorie target based on goal."""
        tdee = self.daily_calories()
        adjustments = {
            Goal.LOSE_WEIGHT: -500,
            Goal.GAIN_MUSCLE: 300,
            Goal.MAINTAIN: 0,
            Goal.CUSTOM: 0,
        }
        return max(1200, tdee + adjustments[self.goal])


class FridgeItem(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    unit: str = "个"
    added_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


class Fridge(BaseModel):
    items: list[FridgeItem] = []
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


class MealItem(BaseModel):
    name: str
    amount: str
    calories: int = 0


class Meal(BaseModel):
    time: str
    name: str
    items: list[MealItem] = []
    total_calories: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0


class DailySummary(BaseModel):
    total_calories: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0


class MealPlan(BaseModel):
    id: str
    date: str
    type: str = "daily"
    goal: str = ""
    meals: list[Meal] = []
    daily_summary: Optional[DailySummary] = None


class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[dict] = None
