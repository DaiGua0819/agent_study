"""
配置模块
"""
import os

# 阿里云 DashScope API Key
# 优先从环境变量读取，如果没有则使用默认值（仅用于本地测试）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-948e99a23fd44f42944e74f102c7be29")

# 默认模型
DEFAULT_MODEL = "qwen-plus"

# 服务配置
HOST = "0.0.0.0"
PORT = 8000
