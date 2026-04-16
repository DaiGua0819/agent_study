"""
测试 API 代码助手
"""
import requests

BASE_URL = "http://localhost:8000/api"


def test_explain():
    """测试代码解释"""
    print("=" * 50)
    print("测试 1: 解释代码")
    print("=" * 50)

    response = requests.post(f"{BASE_URL}/explain", json={
        "code": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
        "detail": "medium"
    })

    print(f"状态码：{response.status_code}")
    print(f"返回结果：\n{response.json()['result'][:200]}...\n")


def test_generate():
    """测试代码生成"""
    print("=" * 50)
    print("测试 2: 生成代码")
    print("=" * 50)

    response = requests.post(f"{BASE_URL}/generate", json={
        "prompt": "写一个判断闰年的函数",
        "style": "pythonic"
    })

    print(f"状态码：{response.status_code}")
    print(f"返回结果：\n{response.json()['result'][:300]}...\n")


def test_fix():
    """测试 Bug 修复"""
    print("=" * 50)
    print("测试 3: 修复 Bug")
    print("=" * 50)

    response = requests.post(f"{BASE_URL}/fix", json={
        "code": "def get_first(lst): return lst[0]",
        "error": "IndexError: list index out of range"
    })

    print(f"状态码：{response.status_code}")
    print(f"返回结果：\n{response.json()['result'][:300]}...\n")


def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("测试 4: 健康检查")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码：{response.status_code}")
    print(f"返回结果：{response.json()}\n")


if __name__ == "__main__":
    print("\n🧪 开始测试 API 代码助手...\n")

    try:
        test_health()
        test_explain()
        test_generate()
        test_fix()
        print("✅ 所有测试完成！")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保 API 服务已启动 (python app.py)")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
