#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import gradio as gr

from image_to_prompt import generate_prompt_from_path


def run_image_to_prompt(image, style: str, purpose: str, model: str) -> tuple[str, str]:
    if image is None:
        return "请先上传图片。", ""

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_path = Path(tmp.name)

    try:
        image.save(temp_path)
        result = generate_prompt_from_path(
            image_path=temp_path,
            model=model or "gpt-4.1-mini",
            style=style.strip() or None,
            purpose=purpose.strip() or None,
        )
        pretty = json.dumps(result, ensure_ascii=False, indent=2)
        main_prompt = result.get("main_prompt", "")
        return pretty, main_prompt
    except Exception as e:  # noqa: BLE001
        return f"处理失败：{e}", ""
    finally:
        temp_path.unlink(missing_ok=True)


with gr.Blocks(title="图片自动转提示词") as demo:
    gr.Markdown("# 图片自动转提示词\n上传图片后，点击按钮即可得到结构化提示词。")
    with gr.Row():
        image_input = gr.Image(type="pil", label="上传图片")
        with gr.Column():
            style_input = gr.Textbox(label="目标风格（可选）", placeholder="比如：电影感 / 动漫 / 写实")
            purpose_input = gr.Textbox(label="用途（可选）", placeholder="比如：Midjourney / 海报 / 电商图")
            model_input = gr.Textbox(label="模型", value="gpt-4.1-mini")
            run_btn = gr.Button("生成提示词", variant="primary")

    json_output = gr.Code(label="完整 JSON 输出", language="json")
    main_prompt_output = gr.Textbox(label="主提示词（可直接复制）", lines=4)

    run_btn.click(
        fn=run_image_to_prompt,
        inputs=[image_input, style_input, purpose_input, model_input],
        outputs=[json_output, main_prompt_output],
    )


if __name__ == "__main__":
    demo.launch()
