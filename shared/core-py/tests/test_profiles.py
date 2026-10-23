import unittest

from modelflare_core.profiles import build_model_profile_index, resolve_model_profile


class ProfilesTest(unittest.TestCase):
    def test_profile_preserves_context_tools_and_vision(self):
        index = build_model_profile_index(
            {
                "openai/gpt-test": {
                    "reasoning": True,
                    "tool_call": True,
                    "temperature_supported": False,
                    "modalities": {"input": ["text", "image"], "output": ["text"]},
                    "limit": {"context": 1_050_000, "input": 922_000, "output": 128_000},
                }
            }
        )
        profile = resolve_model_profile("gpt-test", index)
        self.assertEqual(profile.context_window, 1_050_000)
        self.assertEqual(profile.max_input_tokens, 922_000)
        self.assertEqual(profile.max_output_tokens, 128_000)
        self.assertEqual(profile.input_modalities, ("text", "image"))
        self.assertTrue(profile.tool_calling)
        self.assertTrue(profile.reasoning)
        self.assertFalse(profile.temperature_supported)

    def test_variant_inherits_base_profile(self):
        index = build_model_profile_index(
            {
                "google/gemini-test": {
                    "reasoning": True,
                    "tool_call": True,
                    "modalities": {"input": ["text", "image"], "output": ["text"]},
                    "limit": {"context": 1_048_576, "output": 65_536},
                }
            }
        )
        profile = resolve_model_profile("gemini-test-high", index)
        self.assertEqual(profile.max_input_tokens, 983_040)
        self.assertIn("image", profile.input_modalities)

    def test_gateway_projected_profile_uses_the_same_parser(self):
        index = build_model_profile_index(
            {
                "gpt-projected": {
                    "context_window": 256_000,
                    "max_input_tokens": 224_000,
                    "max_output_tokens": 32_000,
                    "input_modalities": ["text", "image"],
                    "tool_calling": False,
                    "reasoning": True,
                    "temperature_supported": False,
                }
            }
        )
        profile = resolve_model_profile("gpt-projected", index)
        self.assertEqual(profile.context_window, 256_000)
        self.assertEqual(profile.max_input_tokens, 224_000)
        self.assertEqual(profile.max_output_tokens, 32_000)
        self.assertEqual(profile.input_modalities, ("text", "image"))
        self.assertFalse(profile.tool_calling)
        self.assertTrue(profile.reasoning)
        self.assertFalse(profile.temperature_supported)

    def test_unknown_model_gets_conservative_capabilities(self):
        profile = resolve_model_profile("unclassified-new-model")
        self.assertEqual(profile.input_modalities, ("text",))
        self.assertFalse(profile.tool_calling)
        self.assertFalse(profile.reasoning)


if __name__ == "__main__":
    unittest.main()
