from dify_plugin import ModelProvider


class ModelflareProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        # Customizable models only: each model is validated on its own in
        # ModelflareLargeLanguageModel.validate_credentials.
        pass
