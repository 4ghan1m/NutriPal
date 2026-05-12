"""prompt_toolkit input handler with plain-input fallback."""
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from pathlib import Path

PROMPT_STYLE = Style.from_dict({
    "prompt": "#00ff87 bold",
})


class InputHandler:
    def __init__(self, history_file: Path):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._use_prompt_toolkit = True
        try:
            self.session = PromptSession(
                history=FileHistory(str(self.history_file)),
                style=PROMPT_STYLE,
            )
        except Exception:
            self._use_prompt_toolkit = False

    def get_input(self) -> str:
        try:
            if self._use_prompt_toolkit:
                return self.session.prompt(
                    [("class:prompt", "> ")],
                    multiline=False,
                ).strip()
            else:
                return input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
