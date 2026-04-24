# 图片自动转提示词

一个最小可用脚本：把图片自动分析成可直接用于文生图/图生图的提示词结构（JSON）。

## 1) 安装

```bash
pip install openai
```

## 2) 配置 Key

```bash
export OPENAI_API_KEY="你的Key"
```

## 3) 运行

```bash
python image_to_prompt.py ./demo.jpg --style "电影感" --purpose "Midjourney"
```

输出示例（节选）：

```json
{
  "main_prompt": "...",
  "negative_prompt": "...",
  "style_tags": ["...", "..."],
  "camera_or_render": "...",
  "lighting": "...",
  "composition": "...",
  "color_palette": "...",
  "optional_variants": ["...", "...", "..."]
}
```

## 4) 可选参数

- `--model`：模型名（默认 `gpt-4.1-mini`）
- `--style`：目标风格（如：动漫、写实、赛博朋克）
- `--purpose`：用途（如：海报、电商图、社媒封面、MJ）

> 说明：这是命令行版本，便于后续接入 Web 或机器人。
