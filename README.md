# OpenWebUI-Funcs

Functions to enhance Open-WebUI.

## Filter funcs

- `gemini-think-summary.py`: Summarize Gemini reasoning stream and emit status updates. [install](https://openwebui.com/posts/gemini_thinking_summary_adf2d8e8)
- `auto_memory.py`: Extract and manage long-term memories from chats, with per-action status updates.
- `search.py`: A Filter action toggle button that maps to other search/thinking models.
- `think.py`: A Filter action toggle button that maps to other thinking/search models.
- `openwebui-hybrid-thinking/hybrid_thinking.py`: Use a cheap thinking model (e.g. DeepSeek R1/QwQ 32B) to generate reasoning, then feed it to a stronger model for final output to balance cost and performance.


---

用于增强 Open-WebUI 的函数。

- `think.py`: 创建一个 Filter 动作切换按钮，用于映射到其他思考/搜索模型。[安装](https://openwebui.com/posts/gemini_thinking_summary_adf2d8e8)
- `search.py`: 创建一个 Filter 动作切换按钮，用于映射到其他搜索/思考模型。
- `gemini-think-summary.py`: 汇总 Gemini 推理流并发送状态更新。
- `auto_memory.py`: 从对话中提取并管理长期记忆，并按动作逐条发送状态更新。
- `openwebui-hybrid-thinking/hybrid_thinking.py`: 使用更便宜的思考模型（如 DeepSeek R1/QwQ 32B）生成推理，再交给更强的模型输出最终结果，以平衡成本与性能。
