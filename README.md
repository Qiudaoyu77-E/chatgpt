# 图片自动转提示词（网页可直接运行）

你说“不会操作”，这里给你最简单的方式：

## 一次性准备

1. 安装 Python（建议 3.10+）
2. 打开终端进入项目目录后执行：

```bash
pip install -r requirements.txt
```

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
