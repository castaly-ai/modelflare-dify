# Modelflare for Dify

一个 Modelflare **Smart API Key**，在 Dify 里调用你账号可用的全部模型，包括 GPT、Claude、Gemini 等。

## 获取 Smart API Key

1. 注册：https://modelflare.dev/sign-up?utm_source=dify&utm_medium=plugin&utm_campaign=integrations
2. 控制台 API Keys →「Create Smart API Key」，选择路由策略（均衡 / 稳定优先 / 低价优先），之后可随时在 Key 设置里修改。

## 配置

1. 安装插件后，打开 **设置 → 模型供应商 → Modelflare → 添加模型**。
2. 填写你的 Key 可以调用的模型 ID（可在 https://modelflare.dev/pricing 查看）、Smart API Key 和 Base URL：
   - 全球：`https://modelflare.dev/v1`（默认）
   - 国内：`https://origin.modelflare.dev/v1`
   - 或自定义地址
3. 保存时只会用 Key 的授权模型列表（`GET /v1/models?scope=authorized`）校验，不消耗额度。

插件会自动识别所选模型的上下文长度、输出上限、视觉、工具调用和推理能力，只接受提供 OpenAI 兼容 Chat 接口的文本模型。图像、视频、向量、重排以及仅支持其他协议的模型不能误添加为 LLM。

使用 Smart API Key 时，同一个 Key 可以添加任意多个模型，新模型上线无需改 Key。

## 常见问题

- **401**：Key 缺失或无效。请在 https://modelflare.dev/keys 创建 Smart API Key。
- **`model_not_found`**：普通 Key 只能调用其分组内的模型；Smart API Key 可调用你账号可用的全部模型。如果已经是 Smart API Key，说明此模型在你的账号下暂不可用。
- **403 `insufficient_user_quota`**：请在 https://modelflare.dev/billing 充值。

图像和视频生成请使用配套插件 **Modelflare 图像与视频**。
