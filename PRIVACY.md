# Privacy Policy

The Modelflare plugin sends the prompts, messages and parameters of each model call, together with your Modelflare API key, to the Modelflare API (`https://modelflare.dev/v1` or `https://origin.modelflare.dev/v1`, as you configure). It also reads your key's authorized model list from `GET /v1/models?scope=authorized` and model capability metadata from `GET /v1/model-profiles`. The key is never sent by the plugin to a third-party metadata service.

The plugin itself does not collect, store or log any user data. Your API key is stored by Dify as an encrypted credential.

Modelflare processes requests under its own privacy policy: https://modelflare.dev/privacy-policy
