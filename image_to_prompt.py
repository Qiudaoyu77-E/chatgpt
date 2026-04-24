#!/usr/bin/env python3
"""图片自动转提示词（Image -> Prompt）

支持两种使用方式：
1) 命令行：python image_to_prompt.py ./demo.jpg --style "电影感"
2) 被 Web 应用导入：from image_to_prompt import generate_prompt_from_path
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

from openai import OpenAI


SYSTEM_INSTRUCTION = (
    "你是资深提示词工程师。请把输入图片转成高质量中文生图提示词。"
    "输出为 JSON，字段必须包含："
    "main_prompt（主提示词）, negative_prompt（负面词）, style_tags（风格标签数组）, "
    "camera_or_render（镜头或渲染参数）, lighting（光照）, composition（构图）, "
    "color_palette（配色）, optional_variants（3条可选变体）。"
)


def to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        mime_type = "image/jpeg"
    raw = image_path.read_bytes()
    b64 = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def build_user_instruction(style: str | None, purpose: str | None) -> str:
    extra: list[str] = []
    if style:
        extra.append(f"目标风格：{style}")
    if purpose:
        extra.append(f"用途：{purpose}")
    if not extra:
        return "请基于图片内容生成提示词。"
    return "请基于图片内容生成提示词。" + "；".join(extra)


def generate_prompt_from_path(
    image_path: Path,
    model: str = "gpt-4.1-mini",
    style: str | None = None,
    purpose: str | None = None,
) -> dict[str, Any]:
    if not image_path.exists():
        raise FileNotFoundError(f"找不到图片: {image_path}")

    client = OpenAI()
    image_data_url = to_data_url(image_path)
    user_instruction = build_user_instruction(style, purpose)

    resp = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_INSTRUCTION}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_instruction},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            },
        ],
        text={"format": {"type": "json_object"}},
    )

    return json.loads(resp.output_text)


def main() -> None:
    parser = argparse.ArgumentParser(description="图片自动转提示词")
    parser.add_argument("image", type=Path, help="输入图片路径")
    parser.add_argument("--model", default="gpt-4.1-mini", help="使用的模型")
    parser.add_argument("--style", default=None, help="期望风格，如 3D / 动漫 / 写实")
    parser.add_argument("--purpose", default=None, help="用途，如 Midjourney / 海报 / 电商主图")
    args = parser.parse_args()

    result = generate_prompt_from_path(
        image_path=args.image,
        model=args.model,
        style=args.style,
        purpose=args.purpose,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
