"""Conversation orchestrator -- message history, context injection, function-call loop."""
from pathlib import Path
from typing import Callable, Optional
from nutripal.data.store import DataStore
from nutripal.data.models import MealPlan
from nutripal.api.client import DeepSeekClient
from nutripal.core import commands


MAX_HISTORY_TURNS = 20


class ChatManager:
    def __init__(self, store: DataStore, client: DeepSeekClient):
        self.store = store
        self.client = client
        self.messages: list[dict] = []
        self._build_system_message()

    def _build_system_message(self):
        profile = self.store.get_profile()
        fridge = self.store.get_fridge()

        profile_text = ""
        if profile:
            goal_labels = {"lose_weight": "减重", "gain_muscle": "增肌", "maintain": "保持健康", "custom": "自定义"}
            goal_text = goal_labels.get(profile.goal.value, str(profile.goal))
            profile_text = (
                f"## 用户身体档案\n"
                f"- 身高: {profile.height_cm}cm | 体重: {profile.weight_kg}kg | 年龄: {profile.age}岁 | "
                f"性别: {'男' if profile.gender.value == 'male' else '女' if profile.gender.value == 'female' else '其他'}\n"
                f"- 活动水平: {profile.activity_level.value} | 目标: {goal_text}\n"
                f"- 每日推荐摄入: {profile.target_calories()} kcal\n"
                f"- 档案更新于: {profile.updated_at}"
            )

        fridge_text = ""
        if fridge and fridge.items:
            items = [f"- {i.name} x{i.quantity}{i.unit}" for i in fridge.items]
            fridge_text = f"## 冰箱当前库存\n" + "\n".join(items)
        else:
            fridge_text = "## 冰箱当前库存\n冰箱是空的，用户需要先添加食材。"

        system_msg = self.client.build_system_message(profile_text, fridge_text)
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0] = system_msg
        else:
            self.messages.insert(0, system_msg)

    def refresh_context(self):
        self._build_system_message()

    def process(self, user_input: str, on_token: Optional[Callable[[str], None]] = None) -> Optional[str]:
        self.messages.append({"role": "user", "content": user_input})
        self._trim_history()

        for _ in range(3):
            response = self.client.chat(self.messages, stream=True, on_token=on_token)
            self.messages.append(response)

            if response.get("tool_calls"):
                for tc in response["tool_calls"]:
                    func_name = tc["function"]["name"]
                    func_args = tc["function"]["arguments"]
                    result = commands.execute_function_call(func_name, func_args, self.store)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })
                self.refresh_context()
                continue
            else:
                return response.get("content")

        return "抱歉，处理你的请求时遇到了一些问题，请再试一次。"

    def _trim_history(self):
        system_msg = self.messages[0] if self.messages else None
        other_msgs = [m for m in self.messages if m["role"] != "system"]
        if len(other_msgs) > MAX_HISTORY_TURNS * 2:
            other_msgs = other_msgs[-(MAX_HISTORY_TURNS * 2):]
        self.messages = [system_msg] + other_msgs if system_msg else other_msgs
