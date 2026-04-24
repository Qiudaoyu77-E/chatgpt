# 图片自动转提示词（多图融合 + 面部细节模式）

你要的功能已支持：
- ✅ **可上传多张照片**（多图融合，降低单图误差）
- ✅ **面部细节模式选项**（网页勾选“面部细节模式（仅提取人脸）”）
- ✅ **限制级选项**（网页勾选“限制级选项（裸露/色情/情色风险拦截）”）

## 一次性准备

- ✅ **仅针对面部细节生成提示词**（默认 `face` 模式）
- ✅ 可选 `restricted` 安全级别（裸露/色情/情色风险拦截）

## 一次性准备

# 图片自动转提示词（网页可直接运行，支持多模型 API Key）

你反馈“生成图和原图细节差距过大”，这个版本专门做了**高保真增强**：
- 新增 `detail_level`（low/medium/high）
- 输出 `must_keep_details`（必须保留细节清单）
- 输出 `spatial_relations`（空间关系）与 `consistency_notes`（一致性约束）

## 一次性准备

你问得非常对：**不必须是 OpenAI Key**。  
现在已经支持：
- OpenAI
- OpenRouter
- SiliconFlow
- 自定义 OpenAI 兼容接口（custom base URL）
# 图片自动转提示词（网页可直接运行）

你说“不会操作”，这里给你最简单的方式：

## 一次性准备

1. 安装 Python（建议 3.10+）
2. 安装依赖：
2. 打开终端进入项目目录后执行：

```bash
pip install -r requirements.txt
```

## 网页运行（推荐）
---

## 直接网页运行（推荐）

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
2. `提取模式` 选 `face`（默认）
3. `细节保真等级` 选 `high`
4. 生成后优先使用 `面部专用提示词（face_prompt）`
5. 再把 `面部必须保留细节（face_must_keep_details）` 一起粘贴到生图工具

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
启动后打开终端给出的地址（通常 `http://127.0.0.1:7860`）。

网页里填写：
1. 上传图片
2. 选 Provider（openai/openrouter/siliconflow/custom）
3. 填 API Key
4. 如果选 custom，再填 Base URL
5. 模型可选（留空会自动使用默认模型）
6. 点击“生成提示词”

---

## 命令行用法（同样支持多平台）

### OpenAI

```bash
python image_to_prompt.py ./demo.jpg --provider openai --api-key "你的OpenAIKey"
```

### OpenRouter

```bash
python image_to_prompt.py ./demo.jpg --provider openrouter --api-key "你的OpenRouterKey"
```

### 自定义 OpenAI 兼容平台

```bash
python image_to_prompt.py ./demo.jpg --provider custom --base-url "https://your-provider.com/v1" --api-key "你的Key" --model "你的视觉模型名"
```

---

## 注意

- 不同平台的“视觉模型能力”差异很大；如果报错，多数是模型不支持图片输入，请换模型。
- 本工具基于 OpenAI SDK 的兼容接口调用方式，适合大多数 OpenAI-compatible 服务。

## 文件说明

- `web_app.py`：网页版本（支持多平台 Key）
- `image_to_prompt.py`：核心逻辑 + CLI
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
