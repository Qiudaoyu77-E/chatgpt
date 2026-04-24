#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import gradio as gr

from image_to_prompt import PROVIDERS, generate_prompt_from_path, get_provider_config


def run_image_to_prompt(
    image,
    provider: str,
    custom_base_url: str,
    api_key: str,
    style: str,
    purpose: str,
    model: str,
) -> tuple[str, str, str]:
    if image is None:
        return "请先上传图片。", "", ""

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_path = Path(tmp.name)

    try:
        image.save(temp_path)

        provider_cfg = get_provider_config(provider, custom_base_url.strip() or None)
        final_base_url = custom_base_url.strip() or provider_cfg["base_url"]
        final_model = model.strip() or provider_cfg.get("default_model") or "gpt-4.1-mini"

        result = generate_prompt_from_path(
            image_path=temp_path,
            model=final_model,
            style=style.strip() or None,
            purpose=purpose.strip() or None,
            api_key=api_key.strip() or None,
            base_url=final_base_url,
        )
        pretty = json.dumps(result, ensure_ascii=False, indent=2)
        main_prompt = result.get("main_prompt", "")
        debug_info = f"provider={provider} | base_url={final_base_url} | model={final_model}"
        return pretty, main_prompt, debug_info
    except Exception as e:  # noqa: BLE001
        return f"处理失败：{e}", "", ""
    finally:
        temp_path.unlink(missing_ok=True)


provider_choices = [*PROVIDERS.keys(), "custom"]

with gr.Blocks(title="图片自动转提示词（多模型 API）") as demo:
    gr.Markdown(
        "# 图片自动转提示词（支持多平台 API Key）\n"
        "支持 OpenAI / OpenRouter / SiliconFlow / 自定义 OpenAI 兼容接口。"
    )
    with gr.Row():
        image_input = gr.Image(type="pil", label="上传图片")
        with gr.Column():
            provider_input = gr.Dropdown(choices=provider_choices, value="openai", label="Provider")
            custom_base_url_input = gr.Textbox(
                label="自定义 Base URL（仅 custom 必填）",
                placeholder="例如：https://your-provider.com/v1",
            )
            api_key_input = gr.Textbox(label="API Key", type="password", placeholder="可填 OpenAI/OpenRouter 等 Key")
            model_input = gr.Textbox(label="模型（可选，留空自动选默认）", value="")
            style_input = gr.Textbox(label="目标风格（可选）", placeholder="比如：电影感 / 动漫 / 写实")
            purpose_input = gr.Textbox(label="用途（可选）", placeholder="比如：Midjourney / 海报 / 电商图")
            run_btn = gr.Button("生成提示词", variant="primary")

    json_output = gr.Code(label="完整 JSON 输出", language="json")
    main_prompt_output = gr.Textbox(label="主提示词（可直接复制）", lines=4)
    debug_output = gr.Textbox(label="请求参数信息", lines=1)

    run_btn.click(
        fn=run_image_to_prompt,
        inputs=[image_input, provider_input, custom_base_url_input, api_key_input, style_input, purpose_input, model_input],
        outputs=[json_output, main_prompt_output, debug_output],
    )


if __name__ == "__main__":
    demo.launch()
