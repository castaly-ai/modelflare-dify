from collections.abc import Generator
from pathlib import Path

import yaml
from dify_plugin.entities.model import AIModelEntity
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from dify_plugin.errors.model import CredentialsValidateFailedError, InvokeBadRequestError
from dify_plugin.interfaces.model.openai_compatible.llm import OAICompatLargeLanguageModel

from modelflare_core import ModelflareClient, ModelflareError, describe_error

ATTRIBUTION_PLUGIN = "modelflare-dify"
UTM_SOURCE = "dify"
VERSION = yaml.safe_load((Path(__file__).resolve().parents[2] / "manifest.yaml").read_text(encoding="utf-8"))["version"]


def _client(credentials: dict) -> ModelflareClient:
    base_url = (credentials.get("custom_base_url") or "").strip() or credentials.get("region") or "global"
    return ModelflareClient(credentials.get("api_key", ""), ATTRIBUTION_PLUGIN, VERSION, base_url)


def _listed_ids(credentials: dict) -> set[str]:
    return {model.get("id") for model in _client(credentials).list_models()}


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
            listed = model in _listed_ids(credentials)
        except Exception:
            listed = None
        return InvokeBadRequestError(
            describe_error(ModelflareError("model_not_found", str(error)), "en", UTM_SOURCE, model_listed=listed)
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        # Validates against the key's model list only, so saving a model never
        # spends quota on a test completion.
        try:
            listed = model in _listed_ids(credentials)
        except ModelflareError as ex:
            raise CredentialsValidateFailedError(describe_error(ex, "en", UTM_SOURCE)) from ex
        except ValueError as ex:
            raise CredentialsValidateFailedError(str(ex)) from ex
        if not listed:
            raise CredentialsValidateFailedError(
                describe_error(ModelflareError("model_not_found", model), "en", UTM_SOURCE, model_listed=False)
            )

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
        return super().get_customizable_model_schema(model, self._compat_credentials(credentials))
