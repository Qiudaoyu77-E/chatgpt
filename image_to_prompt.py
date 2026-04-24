#!/usr/bin/env python3
"""图片自动转提示词（Image -> Prompt）

支持两种使用方式：
1) 命令行：python image_to_prompt.py ./demo.jpg --style "电影感"
2) 被 Web 应用导入：from image_to_prompt import generate_prompt_from_path

支持多模型/多平台 API Key（OpenAI 兼容接口）。
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


PROVIDERS: dict[str, dict[str, str]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4.1-mini",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openai/gpt-4.1-mini",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-VL-72B-Instruct",
    },
}


def get_provider_config(provider: str, custom_base_url: str | None = None) -> dict[str, str]:
    p = provider.strip().lower()
    if p == "custom":
        if not custom_base_url:
            raise ValueError("provider=custom 时必须提供 base_url")
        return {"base_url": custom_base_url, "default_model": ""}

    if p not in PROVIDERS:
        supported = ", ".join([*PROVIDERS.keys(), "custom"])
        raise ValueError(f"不支持的 provider: {provider}。可选：{supported}")
    return PROVIDERS[p]


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
    model: str | None = None,
    style: str | None = None,
    purpose: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str = "gpt-4.1-mini",
    style: str | None = None,
    purpose: str | None = None,
) -> dict[str, Any]:
    if not image_path.exists():
        raise FileNotFoundError(f"找不到图片: {image_path}")

    client = OpenAI(api_key=api_key, base_url=base_url)
    client = OpenAI()
    image_data_url = to_data_url(image_path)
    user_instruction = build_user_instruction(style, purpose)

    resp = client.responses.create(
        model=model or "gpt-4.1-mini",
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
    parser.add_argument("--provider", default="openai", help="openai/openrouter/siliconflow/custom")
    parser.add_argument("--base-url", default=None, help="provider=custom 时必填；其他 provider 可覆盖默认地址")
    parser.add_argument("--api-key", default=None, help="对应平台 API Key（不传则使用环境变量）")
    parser.add_argument("--model", default=None, help="模型名，不传则用 provider 默认值")
    parser.add_argument("--model", default="gpt-4.1-mini", help="使用的模型")
    parser.add_argument("--style", default=None, help="期望风格，如 3D / 动漫 / 写实")
    parser.add_argument("--purpose", default=None, help="用途，如 Midjourney / 海报 / 电商主图")
    args = parser.parse_args()

    provider_cfg = get_provider_config(args.provider, args.base_url)
    final_base_url = args.base_url or provider_cfg["base_url"]
    final_model = args.model or provider_cfg.get("default_model") or "gpt-4.1-mini"

    result = generate_prompt_from_path(
        image_path=args.image,
        model=final_model,
        style=args.style,
        purpose=args.purpose,
        api_key=args.api_key,
        base_url=final_base_url,
    result = generate_prompt_from_path(
        image_path=args.image,
        model=args.model,
        style=args.style,
        purpose=args.purpose,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
