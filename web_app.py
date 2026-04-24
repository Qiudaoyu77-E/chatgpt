#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from image_to_prompt import PROVIDERS, generate_prompt_from_paths, get_provider_config

CONFIG_PATH = Path.home() / ".image_to_prompt_config.json"


def load_saved_settings() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {k: str(v) for k, v in data.items() if v is not None}
    except Exception:  # noqa: BLE001
        pass
    return {}


def save_settings(settings: dict[str, str]) -> str:
    CONFIG_PATH.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        CONFIG_PATH.chmod(0o600)
    except Exception:  # noqa: BLE001
        pass
    return f"已保存配置到 {CONFIG_PATH}"


def load_settings_for_ui() -> tuple[str, str, str, str, str]:
    settings = load_saved_settings()
    provider = settings.get("provider", "openai")
    base_url = settings.get("base_url", "")
    api_key = settings.get("api_key", "")
    model = settings.get("model", "")
    msg = "已加载保存的配置" if settings else "未找到保存配置"
    return provider, base_url, api_key, model, msg


def run_image_to_prompt(
    files,
    provider: str,
    custom_base_url: str,
    api_key: str,
    style: str,
    purpose: str,
    model: str,
    detail_level: str,
    focus_mode: str,
    safety_level: str,
    remember_settings: bool,
) -> tuple[str, str, str, str, str, str, str, str]:
    if not files:
        return "请至少上传 1 张图片。", "", "", "", "", "", "", ""

    image_paths = [Path(f) for f in files]

    try:
        provider_cfg = get_provider_config(provider, custom_base_url.strip() or None)
        final_base_url = custom_base_url.strip() or provider_cfg["base_url"]
        final_model = model.strip() or provider_cfg.get("default_model") or "gpt-4.1-mini"

        if remember_settings:
            save_msg = save_settings(
                {
                    "provider": provider,
                    "base_url": custom_base_url.strip(),
                    "api_key": api_key.strip(),
                    "model": model.strip(),
                }
            )
        else:
            save_msg = "未保存配置"

        result = generate_prompt_from_paths(
            image_paths=image_paths,
            model=final_model,
            style=style.strip() or None,
            purpose=purpose.strip() or None,
            detail_level=detail_level,
            focus_mode=focus_mode,
            safety_level=safety_level,
            api_key=api_key.strip() or None,
            base_url=final_base_url,
        )
        pretty = json.dumps(result, ensure_ascii=False, indent=2)
        main_prompt = result.get("main_prompt", "")
        face_prompt = result.get("face_prompt", "")
        must_keep = "\n".join(f"- {i}" for i in result.get("must_keep_details", []))
        face_must_keep = "\n".join(f"- {i}" for i in result.get("face_must_keep_details", []))
        country_clues = "\n".join(f"- {i}" for i in result.get("country_or_region_clues", []))
        debug_info = (
            f"images={len(image_paths)} | provider={provider} | base_url={final_base_url} | model={final_model} | "
            f"detail_level={detail_level} | focus_mode={focus_mode} | safety_level={safety_level}"
        )
        return pretty, main_prompt, face_prompt, must_keep, face_must_keep, country_clues, debug_info, save_msg
    except Exception as e:  # noqa: BLE001
        return f"处理失败：{e}", "", "", "", "", "", "", ""


provider_choices = [*PROVIDERS.keys(), "custom"]
saved = load_saved_settings()

with gr.Blocks(title="图片自动转提示词（多图+面部细节）") as demo:
    gr.Markdown(
        "# 图片自动转提示词（支持多图融合，默认仅面部细节）\n"
        "可上传多张人物图，系统会融合共同面部特征，减少单图误差。"
    )
    with gr.Row():
        files_input = gr.File(label="上传图片（可多选）", file_count="multiple", file_types=["image"])
        with gr.Column():
            provider_input = gr.Dropdown(choices=provider_choices, value=saved.get("provider", "openai"), label="Provider")
            custom_base_url_input = gr.Textbox(
                label="自定义 Base URL（仅 custom 必填）",
                placeholder="例如：https://your-provider.com/v1",
                value=saved.get("base_url", ""),
            )
            api_key_input = gr.Textbox(
                label="API Key",
                type="password",
                placeholder="可填 OpenAI/OpenRouter 等 Key",
                value=saved.get("api_key", ""),
            )
            model_input = gr.Textbox(label="模型（可选，留空自动选默认）", value=saved.get("model", ""))
            detail_level_input = gr.Dropdown(choices=["low", "medium", "high"], value="high", label="细节保真等级")
            focus_mode_input = gr.Dropdown(
                choices=["face", "general"],
                value="face",
                label="提取模式",
                info="face=仅面部细节（推荐）",
            )
            safety_level_input = gr.Dropdown(
                choices=["normal", "restricted"],
                value="normal",
                label="使用限制级别",
                info="restricted: 检测到裸露/色情/情色风险将阻止生成",
            )
            style_input = gr.Textbox(label="目标风格（可选）")
            purpose_input = gr.Textbox(label="用途（可选）")
            remember_settings_input = gr.Checkbox(label="记住 API Key 和 Base URL", value=True)
            with gr.Row():
                load_btn = gr.Button("加载已保存配置")
                run_btn = gr.Button("生成提示词", variant="primary")

    json_output = gr.Code(label="完整 JSON 输出", language="json")
    main_prompt_output = gr.Textbox(label="主提示词", lines=4)
    face_prompt_output = gr.Textbox(label="面部专用提示词（推荐复制）", lines=4)
    must_keep_output = gr.Textbox(label="通用必须保留细节", lines=6)
    face_must_keep_output = gr.Textbox(label="面部必须保留细节", lines=8)
    country_output = gr.Textbox(label="国家/地区线索（基于场景证据）", lines=5)
    debug_output = gr.Textbox(label="请求参数信息", lines=2)
    save_state_output = gr.Textbox(label="配置状态", lines=1)

    run_btn.click(
        fn=run_image_to_prompt,
        inputs=[
            files_input,
            provider_input,
            custom_base_url_input,
            api_key_input,
            style_input,
            purpose_input,
            model_input,
            detail_level_input,
            focus_mode_input,
            safety_level_input,
            remember_settings_input,
        ],
        outputs=[
            json_output,
            main_prompt_output,
            face_prompt_output,
            must_keep_output,
            face_must_keep_output,
            country_output,
            debug_output,
            save_state_output,
        ],
    )

    load_btn.click(
        fn=load_settings_for_ui,
        inputs=[],
        outputs=[provider_input, custom_base_url_input, api_key_input, model_input, save_state_output],
    )


if __name__ == "__main__":
    demo.launch()
