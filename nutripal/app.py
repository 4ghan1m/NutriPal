"""Main application REPL loop."""
import sys
from pathlib import Path
from nutripal.data.store import DataStore
from nutripal.api.client import DeepSeekClient
from nutripal.ui.console import (
    console, ACCENT, MUTED, print_banner, print_success,
    print_error, print_info, print_fridge, print_profile,
)
from nutripal.ui.input_handler import InputHandler
from nutripal.core.onboarding import run_onboarding
from nutripal.core.chat import ChatManager


class App:
    def __init__(self, data_dir: Path, config_path: Path):
        self.data_dir = Path(data_dir)
        self.config_path = Path(config_path)
        self.store = DataStore(self.data_dir)
        self.client = None
        self.chat_manager = None

    def run(self):
        try:
            self.client = DeepSeekClient(self.config_path)
        except ValueError as e:
            print_error(str(e))
            print_info("请在 config.json 中填入 deepseek_api_key 后重新启动。")
            sys.exit(1)

        if not self.store.is_onboarding_complete():
            run_onboarding(self.store)

        profile = self.store.get_profile()
        fridge = self.store.get_fridge()
        self.chat_manager = ChatManager(self.store, self.client)

        input_handler = InputHandler(self.data_dir / ".input_history")

        console.clear()
        print_banner(profile, fridge)

        while True:
            try:
                user_input = input_handler.get_input()
            except KeyboardInterrupt:
                console.print("\n")
                continue

            if not user_input:
                console.print(f"\n[{MUTED}]再见！[/{MUTED}]")
                break

            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                console.print(f"[{MUTED}]再见！[/{MUTED}]")
                break

            if user_input.lower() == "/help":
                _print_help()
                continue

            if user_input.lower() == "/fridge":
                print_fridge(self.store.get_fridge())
                continue

            if user_input.lower() == "/profile":
                profile = self.store.get_profile()
                if profile:
                    print_profile(profile)
                continue

            console.print(f"\n[{ACCENT}]NutriPal:[/{ACCENT}]")
            try:
                response = self.chat_manager.process(user_input, on_token=lambda t: console.print(t, end=""))
                if response:
                    console.print()
            except Exception as e:
                console.print()
                print_error(f"请求失败: {e}")
            console.print()


def _print_help():
    console.print(f"""
[{ACCENT}]可用操作：[/{ACCENT}]

  自然语言（推荐） -- 直接跟 AI 对话：
    "冰箱里有3个鸡蛋和一块鸡胸肉，中午吃什么"
    "我刚买了一斤牛肉"          -> AI 自动添加到冰箱
    "鸡蛋吃完了"               -> AI 自动从冰箱移除
    "我最近瘦了2斤"            -> AI 自动更新体重
    "看看冰箱里有什么"          -> AI 展示库存

  快捷命令：
    /fridge    查看冰箱食材清单
    /profile   查看身体信息
    /help      显示此帮助
    /exit      退出程序
""")
