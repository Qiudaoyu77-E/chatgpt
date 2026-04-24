# 图片自动转提示词（多图融合 + 面部细节模式）

你要的功能已支持：
- ✅ **可上传多张照片**（多图融合，降低单图误差）
- ✅ **面部细节模式选项**（网页勾选“面部细节模式（仅提取人脸）”）
- ✅ **限制级选项**（网页勾选“限制级选项（裸露/色情/情色风险拦截）”）

## 一次性准备

```bash
pip install -r requirements.txt
```

## 网页运行（推荐）

```bash
python web_app.py
```

打开 `http://127.0.0.1:7860`（以终端实际输出为准）。

### 推荐流程（高精度面部）

1. 一次上传 3~8 张同一人物照片（角度/表情/光线尽量多样）
2. 勾选“面部细节模式（仅提取人脸）”
3. 如需内容审核，勾选“限制级选项（裸露/色情/情色风险拦截）”
4. `细节保真等级` 选 `high`
5. 生成后优先使用 `面部专用提示词（face_prompt）`
6. 再把 `面部必须保留细节（face_must_keep_details）` 一起粘贴到生图工具

## 命令行示例（多图）

```bash
python image_to_prompt.py img1.jpg img2.jpg img3.jpg \
  --focus-mode face \
  --detail-level high \
  --safety-level normal \
  --provider openai \
  --api-key "你的Key"
```

## 参数说明

- `images`：支持多张图片输入
- `--focus-mode`：`face/general`（默认 `face`）
- `--detail-level`：`low/medium/high`
- `--safety-level`：`normal/restricted`
- `--provider`：`openai/openrouter/siliconflow/custom`
- `--base-url`：custom 时必填
- `--api-key`：对应平台 key

## 国家/地区线索说明

- 输出的是 `country_or_region_clues`（场景证据，如路牌/旗帜/地标）。
- 不会根据人物外貌推断国籍。

## 安全提示

- API Key 会保存在本机 `~/.image_to_prompt_config.json` 文件（若你勾选“记住 API Key 和 Base URL”）。
- 请勿在共享电脑上保存 API Key。


## 快捷命令开关

- `--face-only`：等同 `--focus-mode face`
- `--restricted`：等同 `--safety-level restricted`
