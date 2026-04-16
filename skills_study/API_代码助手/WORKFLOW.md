# API 代码助手 - 详细工作流程

## 目录结构

```
API_代码助手/
├── config.py           # 1. 配置（API Key、模型等）
├── agent.py            # 2. Agent 核心（调用 LLM）
├── app.py              # 3. Flask HTTP 服务
├── agent_demo.py       # 4. Agent 自主调用演示
├── quick_test.py       # 5. 快速测试
└── README.md
```

---

## 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户请求                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  方式 A: HTTP API (app.py)     │  方式 B: 直接调用 (agent_demo.py)  │
├────────────────────────────────┼────────────────────────────────────┤
│  /api/explain                  │  Python 函数直接调用                │
│  /api/generate                 │  Agent 自主决策循环                 │
│  /api/fix                      │                                     │
│  /api/test                     │                                     │
│  /api/chat                     │                                     │
└────────────────────────────────┴────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    agent.py (Agent Core)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  get_agent() → 单例模式                              │    │
│  │  ↓                                                   │    │
│  │  AgentCore.call_llm(prompt)                          │    │
│  │  ↓                                                   │    │
│  │  1. 构建消息 [system, user]                          │    │
│  │  2. 调用 dashscope.Generation.call()                 │    │
│  │  3. 处理响应                                         │    │
│  │  4. 错误重试                                         │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   阿里云 DashScope API                        │
│                    (qwen-plus 模型)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 访问顺序详解

### 方式 A：HTTP API 请求流程

```
用户 → app.py → skill 函数 → agent.py → LLM → 返回
```

#### 示例：解释代码

```python
# 1. 用户发送 HTTP 请求
POST http://localhost:8000/api/explain
{
    "code": "def hello(): print('Hi')",
    "detail": "medium"
}

# ↓ Flask 路由接收 (app.py:13-37)

# 2. 调用 explain_code 函数
def explain_code(code: str, detail: str = "medium") -> str:
    # 根据 detail 构建不同的 prompt
    if detail == 'low':
        prompt = "请用 1-2 句话简单概述..."
    elif detail == 'high':
        prompt = "请详细解释：1...2...3...4...5..."
    else:
        prompt = "请解释：1...2...3..."
    
    prompt += f"\n代码：\n```python\n{code}\n```"
    
    # ↓ 调用 Agent

# 3. 获取 Agent 实例 (agent.py:72-77)
agent = get_agent()
# ↓ 单例模式，只创建一次

# 4. 调用 LLM (agent.py:35-53)
result = agent.call_llm(prompt)
# ↓
# 构建消息：
# [
#   {"role": "system", "content": "你是专业的 Python 代码助手"},
#   {"role": "user", "content": prompt}
# ]
# ↓
# 调用阿里云 API：
# dashscope.Generation.call(model="qwen-plus", messages=..., max_tokens=2000)
# ↓
# 返回 LLM 响应

# 5. 返回 JSON 响应
return jsonify({"success": True, "result": result})
```

---

### 方式 B：Agent 自主调用流程

```
用户输入 → Agent 循环 → LLM 决策 → 解析 JSON → 执行工具 → 返回
```

#### 详细步骤（agent_demo.py）

```python
# 步骤 1：用户输入
user_input = "帮我解释一下这段代码：def hello(): print('Hi')"

# ↓ agent_loop() 被调用

# 步骤 2：构建 System Prompt（包含工具描述）
SYSTEM_PROMPT = """
你是一个智能代码助手 Agent，可以调用工具来完成用户的任务。

## 可用工具
{
    "explain_code": {"description": "解释代码", "params": {...}},
    "generate_code": {...},
    "fix_bug": {...},
    "generate_test": {...}
}

## 调用格式
输出 JSON 格式：
{"action": "工具名", "params": {...}}
"""

# ↓ 第 1 轮循环

# 步骤 3：构建对话历史
messages = [{"role": "user", "content": user_input}]
history = "user: 帮我解释一下这段代码：def hello(): print('Hi')"

# 步骤 4：调用 LLM
prompt = f"{SYSTEM_PROMPT}\n\n对话历史：\n{history}\n\n助手："
response = agent.call_llm(prompt)

# ↓ LLM 分析后，决定调用 explain_code 工具
# LLM 输出：
# ```json
# {
#     "action": "explain_code",
#     "params": {
#         "code": "def hello(): print('Hi')",
#         "detail": "medium"
#     }
# }
# ```

# 步骤 5：解析 LLM 响应
action_data = parse_action(response)
# action_data = {"action": "explain_code", "params": {...}}

# 步骤 6：执行工具
result = execute_action("explain_code", params)
# ↓ 调用本地 explain_code() 函数
# ↓ 内部调用 agent.call_llm() → 阿里云 API

# 步骤 7：将结果加入历史
messages.append({
    "role": "assistant",
    "content": f"我调用了 explain_code，结果是：{result}"
})

# ↓ 如果需要，继续第 2 轮循环...
# ↓ 直到 LLM 直接回复（不输出 JSON），表示任务完成

# 步骤 8：返回最终结果
return response
```

---

## 完整访问顺序图

### HTTP API 模式

```
┌─────────┐     ┌─────────┐     ┌───────────┐     ┌─────────┐     ┌──────────┐
│  用户    │     │ app.py  │     │ skill 函数 │     │ agent.py│     │ DashScope│
└────┬────┘     └────┬────┘     └─────┬─────┘     └────┬────┘     └────┬─────┘
     │               │                 │                 │               │
     │ POST /api/explain               │                 │               │
     │──────────────>│                 │                 │               │
     │               │                 │                 │               │
     │               │ explain_code()  │                 │               │
     │               │────────────────>│                 │               │
     │               │                 │                 │               │
     │               │                 │ get_agent()     │               │
     │               │                 │────────────────>│               │
     │               │                 │                 │               │
     │               │                 │ call_llm(prompt)│               │
     │               │                 │────────────────>│               │
     │               │                 │                 │               │
     │               │                 │                 │ HTTP Request  │
     │               │                 │                 │──────────────>│
     │               │                 │                 │               │
     │               │                 │                 │               │ 生成响应
     │               │                 │                 │<──────────────│
     │               │                 │                 │               │
     │               │                 │ result          │               │
     │               │                 │<────────────────│               │
     │               │                 │                 │               │
     │               │ {"success":...} │                 │               │
     │<──────────────│                 │                 │               │
     │               │                 │                 │               │
```

### Agent 自主调用模式

```
┌─────────┐     ┌───────────────┐     ┌─────────┐     ┌──────────┐
│  用户    │     │ agent_demo.py │     │ agent.py│     │ DashScope│
└────┬────┘     └───────┬───────┘     └────┬────┘     └────┬─────┘
     │                  │                   │               │
     │ 输入需求          │                   │               │
     │─────────────────>│                   │               │
     │                  │                   │               │
     │                  │ 构建 System Prompt │               │
     │                  │ (包含工具描述)     │               │
     │                  │                   │               │
     │                  │ call_llm(prompt)  │               │
     │                  │──────────────────>│               │
     │                  │                   │ HTTP Request  │
     │                  │                   │──────────────>│
     │                  │                   │               │
     │                  │                   │  决策 JSON     │
     │                  │                   │<──────────────│
     │                  │                   │               │
     │                  │ parse_action()    │               │
     │                  │ 解析出 action      │               │
     │                  │                   │               │
     │                  │ execute_action()  │               │
     │                  │ (调用本地函数)     │               │
     │                  │─────────┐         │               │
     │                  │         │         │               │
     │                  │<────────┘         │               │
     │                  │                   │               │
     │                  │ 将结果加入历史     │               │
     │                  │                   │               │
     │                  │ 循环...直到完成    │               │
     │                  │                   │               │
     │ 返回最终结果      │                   │               │
     │<─────────────────│                   │               │
     │                  │                   │               │
```

---

## 调用链总结

### 1. HTTP API 模式（app.py）

```
用户请求
  ↓
Flask 路由 (app.py)
  ↓
技能函数 (explain_code / generate_code / fix_bug / generate_test)
  ↓
Agent 实例 (agent.py)
  ↓
call_llm() → 构建 prompt → 调用 LLM
  ↓
阿里云 DashScope API
  ↓
返回结果 → JSON 响应
```

### 2. Agent 自主调用模式（agent_demo.py）

```
用户输入
  ↓
agent_loop() 循环
  ↓
构建 System Prompt（包含工具描述）
  ↓
LLM 决策 → 输出 JSON
  ↓
parse_action() 解析
  ↓
execute_action() 执行本地函数
  ↓
调用 agent.call_llm()
  ↓
阿里云 DashScope API
  ↓
结果加入历史 → 继续循环或返回
```

---

## 关键文件职责

| 文件 | 职责 | 被调用顺序 |
|------|------|-----------|
| `config.py` | 存储配置（API Key、模型） | 1️⃣ 最先加载 |
| `agent.py` | Agent 核心，调用 LLM | 2️⃣ 被 skill 函数调用 |
| `app.py` | Flask HTTP 服务 | 3️⃣ 接收外部请求 |
| `agent_demo.py` | Agent 自主调用演示 | 3️⃣ 直接调用 agent.py |

---

## 请求处理时序

### HTTP 请求处理

```
时间 →
0ms    用户发送请求
10ms   Flask 接收，路由到对应函数
20ms   构建 skill-specific prompt
30ms   调用 agent.call_llm()
50ms   发送请求到阿里云 API
200ms  阿里云返回 LLM 响应
210ms  返回 JSON 给用户
```

### Agent 自主调用

```
时间 →
0ms     用户输入
10ms    构建 System Prompt
50ms    第 1 次 LLM 调用（决策）
200ms   解析出 action
210ms   执行工具（第 2 次 LLM 调用）
400ms   得到结果
410ms   判断是否继续循环...
```
