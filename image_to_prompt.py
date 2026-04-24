#!/usr/bin/env python3
"""图片自动转提示词（Image -> Prompt）

支持两种使用方式：
1) 命令行：python image_to_prompt.py img1.jpg img2.jpg --focus-mode face
2) 被 Web 应用导入：from image_to_prompt import generate_prompt_from_paths
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

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]
from openai import OpenAI


BASE_SYSTEM_INSTRUCTION = (
    "你是资深提示词工程师，目标是让‘根据提示词再生成的图片’尽量贴近原图。"
    "你必须优先保真，而不是艺术化改写。"
    "默认输出 JSON 字段："
    "main_prompt, negative_prompt, style_tags, camera_or_render, lighting, composition, color_palette, "
    "must_keep_details, spatial_relations, consistency_notes, country_or_region_clues, optional_variants。"
)

FACE_FOCUS_APPEND = (
    "当前任务为 face 模式：只关注面部细节，不描述服装、背景和身体细节。"
    "额外必须输出字段："
    "face_prompt（可直接用于生图的人脸提示词）, "
    "face_must_keep_details（不少于 15 条面部硬约束）, "
    "face_geometry（脸型/五官比例）, eye_details, nose_details, lip_details, skin_texture_details, hairline_hair_details。"
)
    "输出为 JSON，字段必须包含："
    "main_prompt（主提示词）, negative_prompt（负面词）, style_tags（风格标签数组）, "
    "camera_or_render（镜头或渲染参数）, lighting（光照）, composition（构图）, "
    "color_palette（配色）, must_keep_details（必须保留细节数组）, "
    "spatial_relations（空间关系数组）, consistency_notes（一致性约束）, "
    "optional_variants（3条可选变体）。"
)


DETAIL_GUIDANCE = {
    "low": "提取主要元素，细节适中。",
    "medium": "提取主体、材质、颜色、构图与关键细节。",
    "high": "极致保真模式：尽可能保留纹理、比例、方向、层级和细微差异。",
}

PROVIDERS: dict[str, dict[str, str]] = {
    "openai": {"base_url": "https://api.openai.com/v1", "default_model": "gpt-4.1-mini"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "default_model": "openai/gpt-4.1-mini"},
    "siliconflow": {"base_url": "https://api.siliconflow.cn/v1", "default_model": "Qwen/Qwen2.5-VL-72B-Instruct"},
    "high": (
        "极致保真模式：必须尽可能保留对象数量、相对位置、文字内容、服饰纹理、光影方向、"
        "焦段/景别、背景元素层级与前后景关系。"
    ),
}


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


def build_user_instruction(
    style: str | None,
    purpose: str | None,
    detail_level: str,
    focus_mode: str,
    image_count: int,
) -> str:
    guidance = DETAIL_GUIDANCE.get(detail_level, DETAIL_GUIDANCE["high"])
    extra: list[str] = [
        f"细节等级：{detail_level}（{guidance}）",
        f"输入图片数量：{image_count}（请综合多图共同特征，忽略单张偶发偏差）",
    ]
def build_user_instruction(style: str | None, purpose: str | None, detail_level: str) -> str:
    guidance = DETAIL_GUIDANCE.get(detail_level, DETAIL_GUIDANCE["high"])
    extra: list[str] = [f"细节等级：{detail_level}（{guidance}）"]
def build_user_instruction(style: str | None, purpose: str | None) -> str:
    extra: list[str] = []
    if style:
        extra.append(f"目标风格：{style}")
    if purpose:
        extra.append(f"用途：{purpose}")

    if focus_mode == "face":
        extra.append("仅输出面部相关细节，忽略服装/背景/肢体。")
        extra.append("禁止根据人物长相推断国籍。")
    else:
        extra.append("禁止根据人物长相推断国籍；只允许输出场景证据支持的国家/地区线索。")

    return "请基于图片内容生成提示词。" + "；".join(extra)


def detect_adult_risk(client: Any, model: str, image_data_url: str) -> dict[str, Any]:
def detect_adult_risk(client: OpenAI, model: str, image_data_url: str) -> dict[str, Any]:
    moderation_instruction = (
        "判断图片是否包含裸露、色情或情色内容风险。"
        "只输出 JSON: {is_adult: bool, risk_level: low|medium|high, reason: string}"
    )
    resp = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": moderation_instruction},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
        text={"format": {"type": "json_object"}},
    )
    data = json.loads(resp.output_text)
    return {
        "is_adult": bool(data.get("is_adult", False)),
        "risk_level": str(data.get("risk_level", "low")),
        "reason": str(data.get("reason", "")),
    }


def generate_prompt_from_paths(
    image_paths: list[Path],
    extra.append(
        "请把主提示词写成‘尽量可还原原图细节’的形式，并在 must_keep_details 里列出不少于 12 条硬约束。"
    )
    if not extra:
        return "请基于图片内容生成提示词。"
    return "请基于图片内容生成提示词。" + "；".join(extra)


def generate_prompt_from_path(
    image_path: Path,
    model: str | None = None,
    style: str | None = None,
    purpose: str | None = None,
    detail_level: str = "high",
    focus_mode: str = "face",
    safety_level: str = "normal",
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    if not image_paths:
        raise ValueError("至少需要上传 1 张图片")
    for p in image_paths:
        if not p.exists():
            raise FileNotFoundError(f"找不到图片: {p}")

    if OpenAI is None:
        raise ModuleNotFoundError("未安装 openai 包，请先执行: pip install -r requirements.txt")

    final_model = model or "gpt-4.1-mini"
    client = OpenAI(api_key=api_key, base_url=base_url)
    image_data_urls = [to_data_url(p) for p in image_paths]

    if safety_level == "restricted":
        for idx, image_data_url in enumerate(image_data_urls, start=1):
            risk = detect_adult_risk(client, final_model, image_data_url)
            if risk["is_adult"]:
                raise ValueError(
                    f"第 {idx} 张图检测到可能违反裸露/色情/情色防护限制，已阻止生成。"
                    f"风险等级: {risk['risk_level']}，原因: {risk['reason']}"
                )

    user_instruction = build_user_instruction(style, purpose, detail_level, focus_mode, len(image_paths))
    system_instruction = BASE_SYSTEM_INSTRUCTION
    if focus_mode == "face":
        system_instruction = BASE_SYSTEM_INSTRUCTION + FACE_FOCUS_APPEND

    user_content: list[dict[str, str]] = [{"type": "input_text", "text": user_instruction}]
    for img in image_data_urls:
        user_content.append({"type": "input_image", "image_url": img})

    resp = client.responses.create(
        model=final_model,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": system_instruction}]},
            {"role": "user", "content": user_content},
    api_key: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str = "gpt-4.1-mini",
    style: str | None = None,
    purpose: str | None = None,
) -> dict[str, Any]:
    if not image_path.exists():
        raise FileNotFoundError(f"找不到图片: {image_path}")

    client = OpenAI(api_key=api_key, base_url=base_url)
    image_data_url = to_data_url(image_path)
    user_instruction = build_user_instruction(style, purpose, detail_level)

    resp = client.responses.create(
        model=model or "gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": BASE_SYSTEM_INSTRUCTION}],
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
    parser.add_argument("images", nargs="+", type=Path, help="输入图片路径（支持多张）")
    parser.add_argument("image", type=Path, help="输入图片路径")
    parser.add_argument("--provider", default="openai", help="openai/openrouter/siliconflow/custom")
    parser.add_argument("--base-url", default=None, help="provider=custom 时必填；其他 provider 可覆盖默认地址")
    parser.add_argument("--api-key", default=None, help="对应平台 API Key（不传则使用环境变量）")
    parser.add_argument("--model", default=None, help="模型名，不传则用 provider 默认值")
    parser.add_argument("--style", default=None, help="期望风格")
    parser.add_argument("--purpose", default=None, help="用途")
    parser.add_argument("--detail-level", default="high", choices=["low", "medium", "high"], help="细节保真等级")
    parser.add_argument("--focus-mode", default="face", choices=["face", "general"], help="face=仅面部细节")
    parser.add_argument(
        "--safety-level",
        default="normal",
        choices=["normal", "restricted"],
        help="normal=正常生成；restricted=检测到裸露/色情/情色风险则阻止",
    )
    parser.add_argument("--style", default=None, help="期望风格，如 3D / 动漫 / 写实")
    parser.add_argument("--purpose", default=None, help="用途，如 Midjourney / 海报 / 电商主图")
    parser.add_argument("--detail-level", default="high", choices=["low", "medium", "high"], help="细节保真等级")
    parser.add_argument("--model", default="gpt-4.1-mini", help="使用的模型")
    parser.add_argument("--style", default=None, help="期望风格，如 3D / 动漫 / 写实")
    parser.add_argument("--purpose", default=None, help="用途，如 Midjourney / 海报 / 电商主图")
    args = parser.parse_args()

    provider_cfg = get_provider_config(args.provider, args.base_url)
    final_base_url = args.base_url or provider_cfg["base_url"]
    final_model = args.model or provider_cfg.get("default_model") or "gpt-4.1-mini"

    result = generate_prompt_from_paths(
        image_paths=args.images,
    result = generate_prompt_from_path(
        image_path=args.image,
        model=final_model,
        style=args.style,
        purpose=args.purpose,
        detail_level=args.detail_level,
        focus_mode=args.focus_mode,
        safety_level=args.safety_level,
        api_key=args.api_key,
        base_url=final_base_url,
        api_key=args.api_key,
        base_url=final_base_url,
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
