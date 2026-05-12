"""First-launch user profile collection."""
from datetime import datetime
from nutripal.data.models import Profile, Gender, ActivityLevel, Goal
from nutripal.data.store import DataStore
from nutripal.ui.console import console, ACCENT, WARN, print_error


GOAL_CHOICES = {
    "1": Goal.LOSE_WEIGHT,
    "2": Goal.GAIN_MUSCLE,
    "3": Goal.MAINTAIN,
    "4": Goal.CUSTOM,
}

ACTIVITY_CHOICES = {
    "1": ActivityLevel.SEDENTARY,
    "2": ActivityLevel.LIGHT,
    "3": ActivityLevel.MODERATE,
    "4": ActivityLevel.ACTIVE,
    "5": ActivityLevel.VERY_ACTIVE,
}

GENDER_CHOICES = {
    "1": Gender.MALE,
    "2": Gender.FEMALE,
    "3": Gender.OTHER,
}


def run_onboarding(store: DataStore) -> Profile:
    console.print(f"\n[{ACCENT}]欢迎使用 NutriPal！让我先了解你的基本情况。[/{ACCENT}]\n")

    today = datetime.now().strftime("%Y-%m-%d")

    height = _ask_float("1/7  身高（cm）", 100, 250)
    weight = _ask_float("2/7  体重（kg）", 20, 300)
    age = _ask_int("3/7  年龄", 1, 120)

    console.print(f"\n[{WARN}]4/7  性别：[/{WARN}]")
    console.print("     [1] 男  [2] 女  [3] 其他")
    gender = _ask_choice("    选择", GENDER_CHOICES)

    console.print(f"\n[{WARN}]5/7  活动水平：[/{WARN}]")
    console.print("     [1] 久坐（几乎不运动）")
    console.print("     [2] 轻度活动（每周 1-2 次）")
    console.print("     [3] 中等活动（每周 3-5 次）")
    console.print("     [4] 活跃（每周 6-7 次）")
    console.print("     [5] 非常活跃（每天高强度）")
    activity = _ask_choice("    选择", ACTIVITY_CHOICES)

    console.print(f"\n[{WARN}]6/7  当前目标：[/{WARN}]")
    console.print("     [1] 减重  [2] 增肌  [3] 保持健康  [4] 自定义")
    goal = _ask_choice("    选择", GOAL_CHOICES)

    profile = Profile(
        height_cm=height,
        weight_kg=weight,
        age=age,
        gender=gender,
        activity_level=activity,
        goal=goal,
        onboarding_complete=True,
        created_at=today,
        updated_at=today,
    )

    store.save_profile(profile)

    console.print(f"\n[{ACCENT}][OK] 档案创建完成！[/{ACCENT}]")
    console.print(f"   每日推荐摄入: {profile.target_calories()} kcal\n")
    return profile


def _ask_float(prompt: str, min_val: float, max_val: float) -> float:
    while True:
        try:
            raw = input(f"{prompt}: ")
        except (EOFError, KeyboardInterrupt):
            print("\n已取消。")
            import sys; sys.exit(0)
        try:
            val = float(raw)
            if min_val <= val <= max_val:
                return val
            print_error(f"请输入 {min_val}-{max_val} 之间的数值")
        except ValueError:
            print_error("请输入有效的数值")


def _ask_int(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            raw = input(f"{prompt}: ")
        except (EOFError, KeyboardInterrupt):
            print("\n已取消。")
            import sys; sys.exit(0)
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print_error(f"请输入 {min_val}-{max_val} 之间的整数")
        except ValueError:
            print_error("请输入有效的整数")


def _ask_choice(prompt: str, choices: dict) -> object:
    while True:
        try:
            val = input(f"{prompt}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已取消。")
            import sys; sys.exit(0)
        if val in choices:
            return choices[val]
        print_error(f"请输入有效选项 ({', '.join(choices.keys())})")
