# 图片自动转提示词（网页可直接运行，支持多模型 API Key）

你问得非常对：**不必须是 OpenAI Key**。  
现在已经支持：
- OpenAI
- OpenRouter
- SiliconFlow
- 自定义 OpenAI 兼容接口（custom base URL）
# 图片自动转提示词（网页可直接运行）

你说“不会操作”，这里给你最简单的方式：

## 一次性准备

1. 安装 Python（建议 3.10+）
2. 安装依赖：
2. 打开终端进入项目目录后执行：

```bash
pip install -r requirements.txt
```

---

## 直接网页运行（推荐）

```bash
python web_app.py
```

启动后打开终端给出的地址（通常 `http://127.0.0.1:7860`）。

网页里填写：
1. 上传图片
2. 选 Provider（openai/openrouter/siliconflow/custom）
3. 填 API Key
4. 如果选 custom，再填 Base URL
5. 模型可选（留空会自动使用默认模型）
6. 点击“生成提示词”

---

## 命令行用法（同样支持多平台）

### OpenAI

```bash
python image_to_prompt.py ./demo.jpg --provider openai --api-key "你的OpenAIKey"
```

### OpenRouter

```bash
python image_to_prompt.py ./demo.jpg --provider openrouter --api-key "你的OpenRouterKey"
```

### 自定义 OpenAI 兼容平台

```bash
python image_to_prompt.py ./demo.jpg --provider custom --base-url "https://your-provider.com/v1" --api-key "你的Key" --model "你的视觉模型名"
```

---

## 注意

- 不同平台的“视觉模型能力”差异很大；如果报错，多数是模型不支持图片输入，请换模型。
- 本工具基于 OpenAI SDK 的兼容接口调用方式，适合大多数 OpenAI-compatible 服务。

## 文件说明

- `web_app.py`：网页版本（支持多平台 Key）
- `image_to_prompt.py`：核心逻辑 + CLI
3. 配置 OpenAI Key：

```bash
export OPENAI_API_KEY="你的Key"
```

> Windows PowerShell 用：`$env:OPENAI_API_KEY="你的Key"`

---

## 直接网页运行（推荐）

执行：

```bash
python web_app.py
```

启动后终端会显示本地地址（通常是 `http://127.0.0.1:7860`），用浏览器打开即可。

使用步骤：
1. 上传图片
2. 可选填写风格、用途
3. 点击“生成提示词”
4. 复制“主提示词”或完整 JSON

---

## 命令行方式（可选）

```bash
python image_to_prompt.py ./demo.jpg --style "电影感" --purpose "Midjourney"
```

---

## 文件说明

- `web_app.py`：网页版本
- `image_to_prompt.py`：核心逻辑 + 命令行版本
- `requirements.txt`：依赖列表
