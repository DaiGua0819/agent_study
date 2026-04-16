# API 代码助手

基于 Flask 的 HTTP API 服务，提供代码助手功能的 RESTful 接口。

## 与 CLI 版本的区别

| 特性 | CLI 版本 | API 版本 |
|------|----------|----------|
| 调用方式 | 命令行被动调用 | HTTP API 主动调用 |
| 使用场景 | 本地开发辅助 | Web 服务、集成到其他应用 |
| 并发支持 | 否 | 是（可处理多请求） |
| 跨语言调用 | 否 | 是（任何 HTTP 客户端） |
| 部署方式 | 本地运行 | 可部署为服务 |

## 安装

```bash
pip install -r requirements.txt
```

## 配置 API Key

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="sk-your-api-key"

# Linux/Mac
export DASHSCOPE_API_KEY="sk-your-api-key"
```

## 启动服务

```bash
python app.py
```

服务默认运行在 `http://0.0.0.0:8000`

---

## API 接口

### 1. 解释代码

**POST** `/api/explain`

```json
{
  "code": "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
  "detail": "medium"
}
```

### 2. 生成代码

**POST** `/api/generate`

```json
{
  "prompt": "写一个快速排序",
  "style": "pythonic"
}
```

### 3. 修复 Bug

**POST** `/api/fix`

```json
{
  "code": "def get_item(lst, i): return lst[i]",
  "error": "IndexError: list index out of range"
}
```

### 4. 生成测试

**POST** `/api/test`

```json
{
  "code": "def add(a, b): return a + b",
  "framework": "pytest"
}
```

### 5. 多轮对话

**POST** `/api/chat`

```json
{
  "message": "如何优化这段代码？",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### 6. 健康检查

**GET** `/api/health`

---

## 使用示例

### cURL

```bash
# 解释代码
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"Hi\")", "detail": "medium"}'

# 生成代码
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "写一个装饰器缓存函数结果"}'
```

### Python

```python
import requests

# 解释代码
response = requests.post('http://localhost:8000/api/explain', json={
    'code': 'def hello(): print("Hi")',
    'detail': 'medium'
})
print(response.json()['result'])

# 生成代码
response = requests.post('http://localhost:8000/api/generate', json={
    'prompt': '写一个装饰器'
})
print(response.json()['result'])
```

### JavaScript (Fetch)

```javascript
// 解释代码
fetch('http://localhost:8000/api/explain', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        code: 'def hello(): print("Hi")',
        detail: 'medium'
    })
})
.then(r => r.json())
.then(data => console.log(data.result));
```

---

## 测试 API

### 方法 1：快速测试（无需启动 Flask 服务）

```bash
python quick_test.py
```

这会直接测试 API 功能是否正常工作。

### 方法 2：Agent 自主调用演示

```bash
python agent_demo.py
```

这是一个交互式演示，LLM 会自主决定调用哪个工具来完成任务。

### 方法 3：启动 Flask 服务测试

```bash
# 启动服务
python app.py

# 在另一个终端测试
curl http://localhost:8000/api/health
```

---

## 项目结构

```
API_代码助手/
├── app.py              # Flask 应用入口
├── agent.py            # Agent 核心
├── config.py           # 配置
└── requirements.txt    # 依赖
```
