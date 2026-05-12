"""Local command executors triggered by AI function calls."""
import json
from datetime import datetime
from nutripal.data.store import DataStore
from nutripal.data.models import Profile, Goal, ActivityLevel, Gender


def execute_function_call(function_name: str, arguments: str, store: DataStore) -> str:
    args = json.loads(arguments) if arguments else {}

    handlers = {
        "add_to_fridge": _handle_add_to_fridge,
        "remove_from_fridge": _handle_remove_from_fridge,
        "view_fridge": _handle_view_fridge,
        "clear_fridge": _handle_clear_fridge,
        "update_profile": _handle_update_profile,
        "view_profile": _handle_view_profile,
        "view_history": _handle_view_history,
        "generate_plan": _handle_generate_plan,
    }

    handler = handlers.get(function_name)
    if handler:
        return handler(args, store)
    return f"未知操作: {function_name}"


def _handle_add_to_fridge(args: dict, store: DataStore) -> str:
    name = args.get("name", "")
    quantity = float(args.get("quantity", 1))
    unit = args.get("unit", "个")
    fridge = store.add_fridge_item(name, quantity, unit)
    return f"已往冰箱添加 {quantity}{unit} {name}。当前冰箱共 {len(fridge.items)} 种食材。"


def _handle_remove_from_fridge(args: dict, store: DataStore) -> str:
    name = args.get("name", "")
    fridge = store.remove_fridge_item(name)
    return f"已从冰箱移除 {name}。当前冰箱剩 {len(fridge.items)} 种食材。"


def _handle_view_fridge(args: dict, store: DataStore) -> str:
    fridge = store.get_fridge()
    if not fridge.items:
        return "冰箱现在是空的。你可以说「冰箱里加...」来添加食材。"
    items = [f"{i.quantity}{i.unit} {i.name}" for i in fridge.items]
    return "冰箱当前库存：\n" + "\n".join(f"  - {i}" for i in items)


def _handle_clear_fridge(args: dict, store: DataStore) -> str:
    store.clear_fridge()
    return "冰箱已清空。"


def _handle_update_profile(args: dict, store: DataStore) -> str:
    field = args.get("field", "")
    value = args.get("value", "")
    profile = store.get_profile()
    if not profile:
        return "未找到用户档案，请先完成首次设置。"

    field_labels = {
        "weight_kg": "体重",
        "height_cm": "身高",
        "age": "年龄",
        "gender": "性别",
        "activity_level": "活动水平",
        "goal": "目标",
    }

    old_value = getattr(profile, field, None)

    if field in ("weight_kg", "height_cm"):
        new_value = float(value)
    elif field == "age":
        new_value = int(value)
    elif field == "gender":
        try:
            new_value = Gender(value)
        except ValueError:
            return f"无效的性别值: {value}，可选: male, female, other"
    elif field == "activity_level":
        try:
            new_value = ActivityLevel(value)
        except ValueError:
            return f"无效的活动水平: {value}"
    elif field == "goal":
        try:
            new_value = Goal(value)
        except ValueError:
            return f"无效的目标: {value}"
    else:
        return f"不支持的字段: {field}"

    setattr(profile, field, new_value)
    profile.updated_at = datetime.now().strftime("%Y-%m-%d")
    store.save_profile(profile)

    label = field_labels.get(field, field)
    return f"已更新{label}: {old_value} -> {new_value}。新的每日推荐摄入: {profile.target_calories()} kcal。"


def _handle_view_profile(args: dict, store: DataStore) -> str:
    profile = store.get_profile()
    if not profile:
        return "未找到用户档案。"
    goal_labels = {"lose_weight": "减重", "gain_muscle": "增肌", "maintain": "保持健康", "custom": "自定义"}
    activity_labels = {"sedentary": "久坐", "light": "轻度", "moderate": "中等", "active": "活跃", "very_active": "非常活跃"}
    gender_labels = {"male": "男", "female": "女", "other": "其他"}

    return (
        f"用户档案 ({profile.updated_at}):\n"
        f"  身高: {profile.height_cm}cm | 体重: {profile.weight_kg}kg | 年龄: {profile.age}岁\n"
        f"  性别: {gender_labels.get(profile.gender.value, profile.gender.value)} | "
        f"活动水平: {activity_labels.get(profile.activity_level.value, profile.activity_level.value)} | "
        f"目标: {goal_labels.get(profile.goal.value, profile.goal.value)}\n"
        f"  每日推荐摄入: {profile.target_calories()} kcal"
    )


def _handle_view_history(args: dict, store: DataStore) -> str:
    plans = store.get_history(limit=5)
    if not plans:
        return "暂无历史膳食方案。"
    result = f"最近 {len(plans)} 条膳食方案:\n"
    for plan in plans:
        s = plan.daily_summary
        summary = f"{s.total_calories}kcal P{s.protein_g}g C{s.carbs_g}g F{s.fat_g}g" if s else "无数据"
        result += f"  [{plan.date}] {summary} ({plan.goal})\n"
    return result


def _handle_generate_plan(args: dict, store: DataStore) -> str:
    meal_type = args.get("meal_type", "daily")
    preference = args.get("preference", "")
    return (
        f"__GENERATE_PLAN__:{meal_type}:{preference}\n"
        "请基于用户冰箱里的食材和身体目标，生成一份详细的膳食方案。"
        "每餐需要包含：菜品名称、具体食材克数、热量、蛋白质/碳水/脂肪克数。"
    )
