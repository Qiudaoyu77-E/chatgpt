import json
import unittest
from pathlib import Path
from unittest.mock import patch

import image_to_prompt
from image_to_prompt import build_user_instruction, generate_prompt_from_paths, get_provider_config, to_data_url


class FakeResponses:
    def __init__(self, outputs):
        self._outputs = outputs
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        text = self._outputs.pop(0)
        return type("Resp", (), {"output_text": text})


class FakeOpenAI:
    def __init__(self, outputs):
        self.responses = FakeResponses(outputs)


class ImageToPromptTests(unittest.TestCase):
    def test_get_provider_config_openai(self):
        cfg = get_provider_config("openai")
        self.assertIn("base_url", cfg)
        self.assertIn("default_model", cfg)

    def test_get_provider_config_custom_requires_base_url(self):
        with self.assertRaises(ValueError):
            get_provider_config("custom")

    def test_build_user_instruction_face_mode(self):
        text = build_user_instruction("写实", "头像", "high", "face", 3)
        self.assertIn("输入图片数量：3", text)
        self.assertIn("仅输出面部相关细节", text)

    def test_to_data_url(self):
        tmp = Path("./.tmp_test.jpg")
        tmp.write_bytes(b"fake")
        try:
            out = to_data_url(tmp)
            self.assertTrue(out.startswith("data:image/jpeg;base64,"))
        finally:
            tmp.unlink(missing_ok=True)

    def test_generate_prompt_from_paths_offline_mock(self):
        img = Path("./.tmp_face.jpg")
        img.write_bytes(b"fake")
        try:
            fake_client = FakeOpenAI([
                json.dumps(
                    {
                        "main_prompt": "portrait",
                        "face_prompt": "detailed face",
                        "face_must_keep_details": ["sharp eyes"],
                    },
                    ensure_ascii=False,
                )
            ])
            with patch.object(image_to_prompt, "OpenAI", return_value=fake_client):
                out = generate_prompt_from_paths(
                    image_paths=[img],
                    model="mock-model",
                    focus_mode="face",
                )

            self.assertEqual(out["face_prompt"], "detailed face")
            self.assertEqual(len(fake_client.responses.calls), 1)
            self.assertEqual(fake_client.responses.calls[0]["model"], "mock-model")
        finally:
            img.unlink(missing_ok=True)

    def test_generate_prompt_from_paths_restricted_blocked_by_mock(self):
        img = Path("./.tmp_adult.jpg")
        img.write_bytes(b"fake")
        try:
            fake_client = FakeOpenAI(
                [
                    json.dumps({"is_adult": True, "risk_level": "high", "reason": "mocked"}, ensure_ascii=False),
                ]
            )
            with patch.object(image_to_prompt, "OpenAI", return_value=fake_client):
                with self.assertRaises(ValueError):
                    generate_prompt_from_paths(
                        image_paths=[img],
                        model="mock-model",
                        safety_level="restricted",
                    )
        finally:
            img.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
