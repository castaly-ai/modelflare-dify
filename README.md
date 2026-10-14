# Modelflare for Dify

One Modelflare **Smart API Key** for every model available to your account — GPT, Claude, Gemini and more — as a Dify model provider.

## Get a Smart API Key

1. Sign up: https://modelflare.dev/sign-up?utm_source=dify&utm_medium=plugin&utm_campaign=integrations
2. Console → API Keys → **Create Smart API Key**, and pick a routing strategy (Balanced / Stability first / Low price first). You can change the strategy on the key at any time.

## Configure

1. Install the plugin, then open **Settings → Model Provider → Modelflare → Add Model**.
2. Enter a model ID your key can call (see https://modelflare.dev/pricing), your Smart API Key and the base URL:
   - Global: `https://modelflare.dev/v1` (default)
   - China: `https://origin.modelflare.dev/v1`
   - Or a custom base URL
3. Saving checks the model against your key's model list (`GET /v1/models`); it does not spend quota.

With a Smart API Key, add as many models as you like with the same key; new models work without editing the key.

## Troubleshooting

- **401**: the key is missing or invalid. Create a Smart API Key at https://modelflare.dev/keys.
- **`model_not_found`**: a regular key only calls the models of its own group. A Smart API Key calls every model available to your account. If you already use a Smart API Key, that model is not available to your account right now.
- **403 `insufficient_user_quota`**: top up at https://modelflare.dev/billing.

Image and video generation is in the companion plugin **Modelflare Image & Video**.

Source: https://github.com/castaly-ai/modelflare-dify · Docs: https://docs.modelflare.dev/ · Privacy: [PRIVACY.md](PRIVACY.md)

License: MIT © Havenbyte LLC
