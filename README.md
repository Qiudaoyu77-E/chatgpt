# 图片自动转提示词（网页可直接运行，支持多模型 API Key）

你反馈“生成图和原图细节差距过大”，这个版本专门做了**高保真增强**：
- 新增 `detail_level`（low/medium/high）
- 输出 `must_keep_details`（必须保留细节清单）
- 输出 `spatial_relations`（空间关系）与 `consistency_notes`（一致性约束）

## 一次性准备

```bash
pip install -r requirements.txt
```

## 网页运行（推荐）

```bash
python web_app.py
```

打开 `http://127.0.0.1:7860`（以终端实际输出为准）。

建议这样用：
1. `detail_level` 选 `high`
2. 复制 `main_prompt`
3. 把 `must_keep_details` 一并贴到你生图工具里（作为硬约束）
4. 如果仍有偏差，换更强视觉模型（不同平台差异很大）

## 命令行示例

```bash
python image_to_prompt.py ./demo.jpg \
  --provider openai \
  --api-key "你的Key" \
  --detail-level high
```

## 参数说明

- `--provider`：`openai/openrouter/siliconflow/custom`
- `--base-url`：custom 时必填
- `--api-key`：对应平台 key
- `--model`：可选，留空走 provider 默认模型
- `--detail-level`：`low/medium/high`，建议 `high`

## 为什么会“像但不够像”

- 纯文本提示词无法 100% 复现原图像素级细节。
- 但通过“细节硬约束 + 空间关系 + 一致性说明”，可明显减少偏差。
- 若目标是最大还原，建议搭配图生图/参考图权重功能（不同平台名称不同）。
