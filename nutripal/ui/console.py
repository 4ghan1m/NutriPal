"""Rich-based terminal UI utilities."""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from nutripal.data.models import Profile, Fridge, MealPlan

# force_terminal=True bypasses legacy Windows console API (GBK encoding)
# and uses ANSI escape codes, which handle Unicode correctly on Win10+
console = Console(force_terminal=True, legacy_windows=False)

ACCENT = "#00ff87"
WARN = "#ffa500"
ERROR = "#ff4444"
MUTED = "#888888"


def print_banner(profile: Profile, fridge: Fridge):
    goal_labels = {
        "lose_weight": "减重",
        "gain_muscle": "增肌",
        "maintain": "保持健康",
        "custom": "自定义",
    }
    goal_text = goal_labels.get(profile.goal.value if hasattr(profile.goal, 'value') else profile.goal, str(profile.goal))
    item_count = len(fridge.items)
    profile_status = "[OK]" if profile.onboarding_complete else "[!]"

    header = Text()
    header.append(" NutriPal -- AI 营养师", style=f"bold {ACCENT}")
    header.append(" " * 8, style="")
    header.append(f"目标: {goal_text}", style=MUTED)
    header.append(" | ", style=MUTED)
    header.append(f"冰箱: {item_count} 种食材", style=MUTED)
    header.append(" | ", style=MUTED)
    header.append(f"档案: {profile_status}", style=MUTED)

    console.print(Panel(header, border_style=ACCENT))
    console.print(f"[{MUTED}]输入你的问题开始对话，或输入 /exit 退出[/{MUTED}]\n")


def print_meal_plan(plan: MealPlan):
    if plan.daily_summary:
        console.print(f"\n[bold {ACCENT}]全天汇总: {plan.daily_summary.total_calories} kcal[/bold {ACCENT}]")
        console.print(f"   蛋白质 {plan.daily_summary.protein_g}g  碳水 {plan.daily_summary.carbs_g}g  脂肪 {plan.daily_summary.fat_g}g")
        console.print()

    for meal in plan.meals:
        time_icon = _time_icon(meal.time)
        console.print(f"[bold {ACCENT}]{time_icon} {meal.name} ({meal.time}) -- {meal.total_calories} kcal[/bold {ACCENT}]")
        for item in meal.items:
            console.print(f"   - {item.name}  {item.amount}")
        console.print(f"   {'-' * 30}")
        console.print(f"   蛋白质 {meal.protein_g}g  碳水 {meal.carbs_g}g  脂肪 {meal.fat_g}g")
        console.print()


def print_fridge(fridge: Fridge):
    table = Table(title="冰箱库存", border_style=ACCENT)
    table.add_column("食材", style="bold")
    table.add_column("数量", justify="right")
    table.add_column("单位")
    table.add_column("添加日期")

    for item in fridge.items:
        table.add_row(item.name, str(item.quantity), item.unit, item.added_at)

    console.print(table)


def print_profile(profile: Profile):
    goal_labels = {
        "lose_weight": "减重", "gain_muscle": "增肌",
        "maintain": "保持健康", "custom": "自定义",
    }
    activity_labels = {
        "sedentary": "久坐", "light": "轻度活动",
        "moderate": "中等活动", "active": "活跃", "very_active": "非常活跃",
    }
    gender_labels = {"male": "男", "female": "女", "other": "其他"}

    table = Table(title="身体档案", border_style=ACCENT)
    table.add_column("项目", style="bold")
    table.add_column("数值")

    table.add_row("身高", f"{profile.height_cm} cm")
    table.add_row("体重", f"{profile.weight_kg} kg")
    table.add_row("年龄", f"{profile.age} 岁")
    table.add_row("性别", gender_labels.get(profile.gender.value if hasattr(profile.gender, 'value') else profile.gender, str(profile.gender)))
    table.add_row("活动水平", activity_labels.get(profile.activity_level.value if hasattr(profile.activity_level, 'value') else profile.activity_level, str(profile.activity_level)))
    table.add_row("目标", goal_labels.get(profile.goal.value if hasattr(profile.goal, 'value') else profile.goal, str(profile.goal)))
    table.add_row("每日推荐摄入", f"{profile.target_calories()} kcal")
    table.add_row("最后更新", profile.updated_at)

    console.print(table)


def print_error(message: str):
    console.print(f"[{ERROR}][ERROR] {message}[/{ERROR}]")


def print_success(message: str):
    console.print(f"[{ACCENT}][OK] {message}[/{ACCENT}]")


def print_info(message: str):
    console.print(f"[{MUTED}]{message}[/{MUTED}]")


def _time_icon(time_str: str) -> str:
    try:
        hour = int(time_str.split(":")[0])
    except (ValueError, IndexError):
        return "[-]"
    if 5 <= hour < 10:
        return "[早餐]"
    elif 10 <= hour < 14:
        return "[午餐]"
    elif 14 <= hour < 17:
        return "[加餐]"
    else:
        return "[晚餐]"
