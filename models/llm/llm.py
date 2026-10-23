from collections.abc import Generator
from pathlib import Path

import yaml
from dify_plugin.entities.model import AIModelEntity, DefaultParameterName, ModelFeature
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from dify_plugin.errors.model import CredentialsValidateFailedError, InvokeBadRequestError
from dify_plugin.interfaces.model.openai_compatible.llm import OAICompatLargeLanguageModel

from modelflare_core import ModelflareClient, ModelflareError, classify_models, describe_error, needs_catalog, resolve_model_profile
from modelflare_core.client import fetch_catalog

ATTRIBUTION_PLUGIN = "modelflare-dify"
UTM_SOURCE = "dify"
VERSION = yaml.safe_load((Path(__file__).resolve().parents[2] / "manifest.yaml").read_text(encoding="utf-8"))["version"]


def _client(credentials: dict) -> ModelflareClient:
    base_url = (credentials.get("custom_base_url") or "").strip() or credentials.get("region") or "global"
    return ModelflareClient(credentials.get("api_key", ""), ATTRIBUTION_PLUGIN, VERSION, base_url)


def _text_model_ids(credentials: dict) -> set[str]:
    listed = _client(credentials).list_models()
    catalog = fetch_catalog() if needs_catalog(listed) else None
    return {model.id for model in classify_models(listed, catalog) if model.kind == "text" and "openai" in model.endpoints}


class ModelflareLargeLanguageModel(OAICompatLargeLanguageModel):
    """OpenAI-compatible chat on the Modelflare gateway, tagged with the plugin's attribution."""

    def _compat_credentials(self, credentials: dict) -> dict:
        client = _client(credentials)
        return {
            **credentials,
            "endpoint_url": client.base_url,
            "extra_headers": client.attribution_headers(),
            "mode": "chat",
            "function_calling_type": "tool_call",
            "stream_function_calling": "supported",
        }

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> LLMResult | Generator:
        try:
            result = super()._invoke(
                model, self._compat_credentials(credentials), prompt_messages, model_parameters, tools, stop, stream, user
            )
        except Exception as ex:
            raise self._explain(ex, model, credentials) from ex
        if isinstance(result, Generator):
            return self._explain_stream(result, model, credentials)
        return result

    def _explain_stream(self, chunks: Generator, model: str, credentials: dict) -> Generator:
        try:
            yield from chunks
        except Exception as ex:
            raise self._explain(ex, model, credentials) from ex

    def _explain(self, error: Exception, model: str, credentials: dict) -> Exception:
        """Replaces a model_not_found failure with the Smart API Key guidance."""
        if "model_not_found" not in str(error):
            return error
        try:
            listed = model in _text_model_ids(credentials)
        except Exception:
            listed = None
        return InvokeBadRequestError(
            describe_error(ModelflareError("model_not_found", str(error)), "en", UTM_SOURCE, model_listed=listed)
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        # Validates against the key's classified text-model list only, so
        # saving never spends quota and media models cannot be registered as LLMs.
        try:
            listed = model in _text_model_ids(credentials)
        except ModelflareError as ex:
            raise CredentialsValidateFailedError(describe_error(ex, "en", UTM_SOURCE)) from ex
        except ValueError as ex:
            raise CredentialsValidateFailedError(str(ex)) from ex
        if not listed:
            raise CredentialsValidateFailedError(
                describe_error(ModelflareError("model_not_found", model), "en", UTM_SOURCE, model_listed=False)
            )

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
        try:
            profiles = _client(credentials).model_profiles()
        except ModelflareError:
            profiles = {}
        profile = resolve_model_profile(model, profiles)
        resolved_credentials = {
            **self._compat_credentials(credentials),
            "context_size": str(profile.context_window),
            "max_tokens_to_sample": str(profile.max_output_tokens),
            "vision_support": "support" if "image" in profile.input_modalities else "not_support",
            "function_calling_type": "tool_call" if profile.tool_calling else "no_call",
            "stream_function_calling": "supported" if profile.tool_calling else "not_supported",
        }
        entity = super().get_customizable_model_schema(model, resolved_credentials)
        features = list(entity.features or [])
        if profile.reasoning and ModelFeature.AGENT_THOUGHT not in features:
            features.append(ModelFeature.AGENT_THOUGHT)
        entity.features = features
        if not profile.temperature_supported:
            unsupported_sampling = {
                DefaultParameterName.TEMPERATURE.value,
                DefaultParameterName.TOP_P.value,
                DefaultParameterName.FREQUENCY_PENALTY.value,
                DefaultParameterName.PRESENCE_PENALTY.value,
            }
            entity.parameter_rules = [rule for rule in entity.parameter_rules if rule.name not in unsupported_sampling]
        for rule in entity.parameter_rules:
            if rule.name == DefaultParameterName.MAX_TOKENS.value:
                rule.max = profile.max_output_tokens
                rule.default = min(rule.default or 512, profile.max_output_tokens)
        return entity
