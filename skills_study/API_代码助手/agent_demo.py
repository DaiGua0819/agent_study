"""
Agent 自主调用示例

模拟一个完整的 Agent 循环：
1. 接收用户任务
2. LLM 分析并决定调用哪个工具
3. 执行工具调用
4. 返回结果给用户
"""
import json
import re
from agent import get_agent

# 获取 Agent 实例
agent = get_agent()

# 定义可用工具
TOOLS = {
    "explain_code": {
        "description": "解释代码的功能、逻辑和用法",
        "params": {
            "code": "要解释的 Python 代码",
            "detail": "详细程度：low/medium/high"
        },
        "endpoint": "/api/explain"
    },
    "generate_code": {
        "description": "根据需求生成 Python 代码",
        "params": {
            "prompt": "代码需求描述",
            "style": "代码风格：pythonic/verbose/minimal"
        },
        "endpoint": "/api/generate"
    },
    "fix_bug": {
        "description": "分析并修复代码中的 bug",
        "params": {
            "code": "有问题的代码",
            "error": "错误信息"
        },
        "endpoint": "/api/fix"
    },
    "generate_test": {
        "description": "为代码生成单元测试",
        "params": {
            "code": "要测试的代码",
            "framework": "测试框架：pytest/unittest"
        },
        "endpoint": "/api/test"
    }
}

# 系统 Prompt - 让 LLM 学会使用工具
SYSTEM_PROMPT = f"""
你是一个智能代码助手 Agent，可以调用工具来完成用户的任务。

## 可用工具

{json.dumps(TOOLS, indent=2, ensure_ascii=False)}

## 调用格式

当你需要调用工具时，请输出 JSON 格式（只输出 JSON，不要其他内容）：

```json
{{
    "action": "工具名称",
    "params": {{
        "参数名": "参数值"
    }}
}}
```

## 工作流程

1. 分析用户请求
2. 判断是否需要调用工具
3. 如果需要，输出 JSON 调用工具
4. 如果不需要，直接回复用户

## 示例

用户：解释一下 def hello(): print('Hi')
助手：
```json
{{
    "action": "explain_code",
    "params": {{
        "code": "def hello(): print('Hi')",
        "detail": "medium"
    }}
}}
```
"""


def parse_action(response: str) -> dict:
    """从 LLM 响应中解析出行动"""
    # 尝试提取 JSON
    match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # 尝试直接解析
    try:
        return json.loads(response)
    except:
        pass

    return None


def execute_action(action: str, params: dict) -> str:
    """执行行动（调用本地方法）"""
    from app import explain_code, generate_code, fix_bug, generate_test

    actions_map = {
        "explain_code": lambda p: explain_code(p.get('code'), p.get('detail', 'medium')),
        "generate_code": lambda p: generate_code(p.get('prompt'), p.get('style', 'pythonic')),
        "fix_bug": lambda p: fix_bug(p.get('code'), p.get('error', '')),
        "generate_test": lambda p: generate_test(p.get('code'), p.get('framework', 'pytest'))
    }

    if action in actions_map:
        return actions_map[action](params)

    return f"未知行动：{action}"


def agent_loop(user_input: str, max_turns: int = 3):
    """
    Agent 主循环

    Args:
        user_input: 用户输入
        max_turns: 最大循环次数
    """
    print(f"\n👤 用户：{user_input}")
    print("-" * 60)

    messages = [{"role": "user", "content": user_input}]

    for turn in range(max_turns):
        print(f"\n🔄 第 {turn + 1} 轮思考...")

        # 构建对话历史
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        # 调用 LLM
        prompt = f"{SYSTEM_PROMPT}\n\n对话历史：\n{history}\n\n助手："
        response = agent.call_llm(prompt, max_tokens=1500)

        print(f"🤖 LLM 响应：{response[:200]}...")

        # 解析行动
        action_data = parse_action(response)

        if action_data and "action" in action_data:
            action = action_data["action"]
            params = action_data.get("params", {})

            print(f"🔧 执行行动：{action}")
            print(f"📦 参数：{params}")

            # 执行行动
            result = execute_action(action, params)

            print(f"✅ 结果：{result[:200]}...")

            # 将结果加入历史
            messages.append({
                "role": "assistant",
                "content": f"我调用了 {action}，结果是：{result}"
            })
        else:
            # LLM 直接回复，不需要调用工具
            print(f"💬 直接回复：{response}")
            return response

    return "达到最大循环次数"


# 本地 API 调用函数（不依赖 Flask）
def explain_code(code: str, detail: str = "medium") -> str:
    """解释代码"""
    if detail == 'low':
        prompt = f"请用 1-2 句话简单概述这段代码的功能：\n```python\n{code}\n```"
    elif detail == 'high':
        prompt = f"""请详细解释以下代码：
1. 功能概述
2. 关键逻辑
3. 输入输出
4. 使用示例
5. 潜在问题

代码：
```python
{code}
```"""
    else:
        prompt = f"""请解释以下代码：
1. 功能概述
2. 关键逻辑
3. 输入输出

代码：
```python
{code}
```"""

    return agent.call_llm(prompt)


def generate_code(prompt: str, style: str = "pythonic") -> str:
    """生成代码"""
    style_instruction = {
        "pythonic": "代码要 Pythonic，简洁优雅",
        "verbose": "代码要详细，包含完整的注释和错误处理",
        "minimal": "代码要尽可能简洁，只保留核心逻辑"
    }

    full_prompt = f"""请帮我生成 Python 代码：
{style_instruction.get(style, '代码要简洁优雅')}

需求：{prompt}

要求：
- 包含完整的类型注解
- 添加必要的 docstring
- 考虑边界情况和错误处理
"""

    return agent.call_llm(full_prompt)


def fix_bug(code: str, error: str = "") -> str:
    """修复 Bug"""
    error_info = error if error else "运行结果不符合预期"

    prompt = f"""请帮我分析并修复以下代码的问题：

**代码**：
```python
{code}
```

**错误信息**：
{error_info}

请：
1. 分析错误原因
2. 给出修复后的完整代码
3. 解释为什么这样修复
"""

    return agent.call_llm(prompt)


def generate_test(code: str, framework: str = "pytest") -> str:
    """生成测试"""
    framework_instruction = {
        "pytest": "使用 pytest 框架，简洁的断言风格",
        "unittest": "使用 Python 内置的 unittest 框架"
    }

    prompt = f"""请为以下代码生成单元测试：

```python
{code}
```

**要求**：
- 使用 {framework_instruction.get(framework, 'pytest')}
- 覆盖正常情况和边界情况
- 包含必要的断言
- 测试函数命名清晰
"""

    return agent.call_llm(prompt)


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Agent 自主调用系统 - 演示")
    print("=" * 60)
    print("\n💡 输入 q 退出\n")

    while True:
        try:
            user_input = input("👤 请输入你的需求：").strip()

            if user_input.lower() in ['q', 'quit', 'exit']:
                print("👋 再见！")
                break

            if not user_input:
                continue

            # 运行 Agent 循环
            result = agent_loop(user_input)

            print("\n" + "=" * 60)
            print(f"📝 最终回复：{result}")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")
