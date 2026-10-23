import unittest

from modelflare_core.media import generate_image
from modelflare_core.models import ClassifiedModel


class _Response:
    def json(self):
        return {"data": [{"b64_json": "aW1hZ2U="}]}


class _Client:
    def __init__(self):
        self.body = None

    def request(self, _method, _path, *, json=None, **_kwargs):
        self.body = json
        return _Response()


class MediaTest(unittest.TestCase):
    def test_selected_model_and_prompt_cannot_be_overridden(self):
        client = _Client()
        model = ClassifiedModel("image-model", "image", ("image-generation",), "images")

        generate_image(
            client,
            model,
            "selected prompt",
            {"model": "wrong-model", "prompt": "wrong prompt", "size": "1024x1024"},
        )

        self.assertEqual(
            client.body,
            {"model": "image-model", "prompt": "selected prompt", "size": "1024x1024"},
        )

    def test_native_gemini_image_rejects_edit_mode(self):
        client = _Client()
        model = ClassifiedModel("gemini-image", "image", ("gemini",), "gemini-generate-content")

        with self.assertRaisesRegex(ValueError, "does not use the OpenAI-compatible image edits route"):
            generate_image(client, model, "test", edit=True)


if __name__ == "__main__":
    unittest.main()
