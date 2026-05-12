# NutriPal — 终端里的 AI 营养师

NutriPal 是一个运行在 Windows 终端中的 AI 营养师，接入 DeepSeek V4 Pro 大模型。你告诉它冰箱里有什么、身体目标是什么，它给你带营养学分析的膳食方案。

## 特性

- **自然语言交互** — 像跟真人营养师聊天一样，无需记忆命令
- **虚拟冰箱** — 持久化食材清单，「冰箱里加3个鸡蛋」→ AI 自动更新库存
- **智能意图识别** — 基于 DeepSeek Function Calling，自动判断用户是要操作数据还是营养咨询
- **长期记忆** — 首次启动收集身体信息（身高/体重/年龄/目标等），作为长期档案主导后续计划
- **营养深度分析** — 膳食方案含分时段安排、食材克数、热量、蛋白质/碳水/脂肪配比
- **双击即用** — PyInstaller 打包成单个 `.exe`，无需安装 Python

## 快速开始

### 方式一：直接运行 exe（推荐）

1. 下载 `dist/NutriPal/` 整个文件夹
2. 在 `config.json` 中填入你的 [DeepSeek API Key](https://platform.deepseek.com/)
3. 双击 `NutriPal.exe`

### 方式二：源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 编辑 config.json，填入 API Key

# 运行
python main.py
```

### 打包为 exe

```bash
python build.py
# 输出在 dist/NutriPal/
```

## 使用示例

```
> 冰箱里有3个鸡蛋、一块鸡胸肉和一颗西兰花，我中午吃什么

NutriPal:
  根据你的减重目标和冰箱食材，推荐以下方案：

  [午餐] 午餐 (12:00) -- 520 kcal
   - 香煎鸡胸肉 150g
   - 蒜蓉西兰花 200g
   - 蒸蛋羹 2个鸡蛋
   ------------------------------
   蛋白质 45g  碳水 18g  脂肪 22g

> 我最近瘦了2斤

NutriPal: 已更新体重: 75.0 -> 74.0kg。新的每日推荐摄入: 2069 kcal。

> 鸡蛋吃完了

NutriPal: 已从冰箱移除 鸡蛋。当前冰箱剩 2 种食材。
```

## 项目结构

```
NutriPal/
├── main.py                     # 入口
├── config.json                 # API Key 配置
├── build.py                    # PyInstaller 打包脚本
├── requirements.txt
├── nutripal/
│   ├── app.py                  # 主 REPL 循环
│   ├── data/
│   │   ├── models.py           # Pydantic 数据模型（含 BMR/TDEE 计算）
│   │   └── store.py            # JSON 持久化存储
│   ├── api/
│   │   └── client.py           # DeepSeek API + Function Calling + 流式
│   ├── ui/
│   │   ├── console.py          # Rich 终端 UI
│   │   └── input_handler.py    # prompt_toolkit 输入（带回退）
│   └── core/
│       ├── onboarding.py       # 首次启动 7 题问卷
│       ├── commands.py         # 8 个 Function 本地执行器
│       └── chat.py             # 对话编排（上下文注入 + Function Loop）
├── data/                       # 运行时数据（自动生成）
└── dist/NutriPal/              # exe 打包输出（可选上传为 Release）
```

## 技术栈

| 层 | 技术 |
|----|------|
| 语言 | Python 3.11+ |
| AI 接入 | DeepSeek API（OpenAI 兼容，Function Calling） |
| 终端 UI | Rich + prompt_toolkit |
| 数据存储 | 本地 JSON |
| 打包 | PyInstaller onedir |

## License

MIT
