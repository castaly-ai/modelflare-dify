"""A misclassified model is sent to the wrong route and fails for the user,
e.g. a Gemini image model offered as a chat model. Shapes follow
GET /v1/models and GET /api/pricing."""

import unittest

from modelflare_core.models import classify_models

MODELS = [
    {"id": "gemini-3-pro-image", "supported_endpoint_types": ["gemini"]},
    {"id": "gemini-3-pro", "supported_endpoint_types": ["gemini", "openai"]},
    {"id": "gpt-image-2", "supported_endpoint_types": ["image-generation", "openai"]},
    {"id": "seedance-2.5", "supported_endpoint_types": ["openai-video"]},
    {"id": "jev-decisions", "supported_endpoint_types": ["decisions"]},
    {"id": "gemini-4-flash-image", "supported_endpoint_types": ["gemini"]},
]
CATALOG = [
    {"model_name": "gemini-3-pro-image", "supported_endpoint_types": ["gemini"], "media_options": {"image": {}}},
    {"model_name": "gemini-3-pro", "supported_endpoint_types": ["gemini", "openai"]},
]


def kinds(catalog):
    return {m.id: f"{m.kind}:{m.image_route}" if m.image_route else m.kind for m in classify_models(MODELS, catalog)}


class ClassifyTest(unittest.TestCase):
    def test_gemini_image_goes_to_generate_content(self):
        result = kinds(CATALOG)
        self.assertEqual(result["gemini-3-pro-image"], "image:gemini-generate-content")
        self.assertEqual(result["gemini-3-pro"], "text")
        self.assertEqual(result["gpt-image-2"], "image:images")
        self.assertEqual(result["seedance-2.5"], "video")
        self.assertNotIn("jev-decisions", result)

    def test_unknown_gemini_only_model_is_hidden_not_chat(self):
        self.assertNotIn("gemini-4-flash-image", kinds(CATALOG))
        self.assertNotIn("gemini-3-pro-image", kinds(None))


if __name__ == "__main__":
    unittest.main()
