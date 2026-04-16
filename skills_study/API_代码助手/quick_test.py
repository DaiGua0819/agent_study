"""
快速测试 API 是否工作
"""
from agent_demo import agent_loop

print("=" * 60)
print("🧪 快速测试 API 代码助手")
print("=" * 60)

# 测试用例
test_cases = [
    ("解释代码", "解释一下这段代码：def hello(): print('Hi')"),
    ("生成代码", "写一个判断闰年的函数"),
    ("修复 Bug", "这段代码有问题：def first(lst): return lst[0]，报错 IndexError"),
    ("生成测试", "为这个函数生成测试：def add(a, b): return a + b")
]

for name, case in test_cases:
    print(f"\n{'='*60}")
    print(f"📋 测试：{name}")
    print(f"{'='*60}")

    try:
        result = agent_loop(case)
        print(f"\n✅ {name} 测试通过")
    except Exception as e:
        print(f"\n❌ {name} 测试失败：{e}")

print("\n" + "=" * 60)
print("🎉 所有测试完成！")
print("=" * 60)
