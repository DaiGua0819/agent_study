"""
模拟 LLM 自主调用 API 的测试

场景：给 LLM 一个任务，让它决定调用哪个 API 来完成
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 定义工具描述（类似 Function Calling）
TOOLS_DESCRIPTION = """
你有以下工具可用：

1. explain_code(code, detail) - 解释代码
   参数：code (代码字符串), detail (low/medium/high)

2. generate_code(prompt, style) - 生成代码
   参数：prompt (需求描述), style (pythonic/verbose/minimal)

3. fix_bug(code, error) - 修复 Bug
   参数：code (代码), error (错误信息)

4. generate_test(code, framework) - 生成测试
   参数：code (代码), framework (pytest/unittest)

当用户请求时，请判断需要调用哪个工具，并以 JSON 格式返回：
{"action": "工具名", "params": {...}}
"""


def call_api(action: str, params: dict) -> str:
    """实际调用 API"""
    endpoint_map = {
        "explain_code": "/explain",
        "generate_code": "/generate",
        "fix_bug": "/fix",
        "generate_test": "/test"
    }

    url = f"{BASE_URL}{endpoint_map.get(action)}"
    response = requests.post(url, json=params)
    return response.json()["result"]


def simulate_llm_task(user_request: str):
    """
    模拟 LLM 接收任务 → 决定调用 API → 执行
    """
    print(f"\n📝 用户请求：{user_request}")
    print("-" * 50)

    # 步骤 1：让 LLM 决定调用哪个 API（这里简化为手动解析）
    # 实际项目中这里会调用 LLM 来决定
    if "解释" in user_request or "explain" in user_request.lower():
        action = "explain_code"
        params = {"code": "def hello(): print('Hi')", "detail": "medium"}
    elif "生成" in user_request or "写一个" in user_request:
        action = "generate_code"
        params = {"prompt": "判断闰年函数", "style": "pythonic"}
    elif "修复" in user_request or "bug" in user_request.lower():
        action = "fix_bug"
        params = {"code": "lst[0]", "error": "IndexError"}
    else:
        print("⚠️  无法判断需求，使用默认：解释代码")
        action = "explain_code"
        params = {"code": "print('test')", "detail": "low"}

    print(f"🤖 LLM 决定调用：{action}")
    print(f"📦 参数：{params}")

    # 步骤 2：调用 API
    try:
        result = call_api(action, params)
        print(f"✅ API 调用成功！")
        print(f"📄 结果：{result[:200]}...")
    except Exception as e:
        print(f"❌ API 调用失败：{e}")


if __name__ == "__main__":
    print("🧪 模拟 LLM 自主调用 API 测试\n")

    # 测试场景
    test_cases = [
        "帮我解释一下这段代码",
        "写一个判断闰年的函数",
        "修复这个 bug"
    ]

    for case in test_cases:
        simulate_llm_task(case)
        print()
