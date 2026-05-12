"""DeepSeek API client with Function Calling and streaming support."""
import json
from pathlib import Path
from typing import Optional, Callable
from openai import OpenAI

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_to_fridge",
            "description": "向虚拟冰箱添加食材",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "食材名称"},
                    "quantity": {"type": "number", "description": "数量"},
                    "unit": {"type": "string", "description": "单位，如个、斤、克、块"}
                },
                "required": ["name", "quantity", "unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_from_fridge",
            "description": "从虚拟冰箱移除食材",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "要移除的食材名称"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_fridge",
            "description": "查看冰箱里当前所有食材",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_fridge",
            "description": "清空冰箱所有食材",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_profile",
            "description": "更新用户身体信息（体重、身高、年龄、目标等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "enum": ["weight_kg", "height_cm", "age", "gender", "activity_level", "goal"],
                        "description": "要更新的字段"
                    },
                    "value": {"type": "string", "description": "新的值"}
                },
                "required": ["field", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_profile",
            "description": "查看用户当前身体信息",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_history",
            "description": "查看历史膳食方案",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_plan",
            "description": "生成膳食方案（基于冰箱食材和用户目标）",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_type": {
                        "type": "string",
                        "enum": ["daily", "weekly", "single_meal"],
                        "description": "方案类型"
                    },
                    "preference": {"type": "string", "description": "用户偏好，如低卡、高蛋白"}
                },
                "required": ["meal_type"]
            }
        }
    }
]

SYSTEM_PROMPT = """你是 NutriPal，一位专业、友好的 AI 营养师，运行在终端中。

你的用户告诉了你冰箱里有什么食材、身体信息（身高/体重/年龄/性别/活动水平）和健康目标。

你的职责：
1. 基于用户冰箱里的食材和身体目标，给出带营养学分析的膳食方案
2. 每份方案包含：分时段（早/午/晚/加餐）、菜品名称、食材克数、热量、蛋白质/碳水/脂肪克数
3. 回答营养学相关问题
4. 减肥场景下给出每周食谱框架、每日进餐时间、每餐份量
5. 当用户表达需要更新冰箱、身体信息时，调用对应的 function 来执行操作

你的风格：专业但不刻板，简洁但有用。回答使用中文。"""


class DeepSeekClient:
    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        api_key = config.get("deepseek_api_key", "").strip()
        base_url = config.get("deepseek_base_url", "https://api.deepseek.com/v1")
        self.model = config.get("model", "deepseek-chat")
        if not api_key:
            raise ValueError(
                "DeepSeek API Key 未配置。请在 config.json 中填入你的 API Key。"
            )
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(
        self,
        messages: list[dict],
        stream: bool = True,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=stream,
            temperature=0.7,
            max_tokens=4096,
        )

        if stream:
            return self._handle_stream(response, on_token)
        else:
            return self._handle_non_stream(response)

    def _handle_stream(self, response, on_token) -> dict:
        collected_content = ""
        tool_call_buffer = {}
        final_message = {"role": "assistant", "content": None}

        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta is None:
                continue

            if delta.content:
                collected_content += delta.content
                if on_token:
                    on_token(delta.content)

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_call_buffer:
                        tool_call_buffer[idx] = {
                            "id": tc.id or "",
                            "function": {"name": "", "arguments": ""}
                        }
                    if tc.id:
                        tool_call_buffer[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_call_buffer[idx]["function"]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_call_buffer[idx]["function"]["arguments"] += tc.function.arguments

        if tool_call_buffer:
            collected_tool_calls = [
                {"id": v["id"], "type": "function", "function": v["function"]}
                for v in sorted(tool_call_buffer.values(), key=lambda x: list(tool_call_buffer.keys())[list(tool_call_buffer.values()).index(x)])
            ]
            final_message["tool_calls"] = collected_tool_calls
        else:
            final_message["content"] = collected_content

        return final_message

    def _handle_non_stream(self, response) -> dict:
        msg = response.choices[0].message
        result = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in msg.tool_calls
            ]
            result["content"] = None
        return result

    def build_system_message(self, profile_text: str, fridge_text: str) -> dict:
        content = SYSTEM_PROMPT
        if profile_text:
            content += "\n\n" + profile_text
        if fridge_text:
            content += "\n\n" + fridge_text
        return {"role": "system", "content": content}
