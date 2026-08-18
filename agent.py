"""
hayabusa-chick: 早押しクイズエージェント

改造するのはこのファイルだけです。

predict_answer() は、問題文が少しずつ読み上げられるたびに呼び出されます。
まだ問題文が最後まで読まれていなくても、確信が持てなくても構わないので、
その時点で最も可能性が高いと思う解答を常に1つ返してください。

使うLLMは .env の LLM_PROVIDER で切り替えます(openai / anthropic / gemini)。
モデル名は LLM_MODEL で変更できます。未設定なら各プロバイダのデフォルトを使います。
APIキーは .env に設定し、os.getenv("...") で読み込みます。

回答が正解かどうかの自動判定は行いません。表示された回答が正しいかどうかは、
実行している人が自分の目で確認してください。
"""

import os
from typing import Optional

_SYSTEM_PROMPT = (
    "あなたは早押しクイズの回答者です。"
    "問題文はまだ最後まで読み終わっていない途中の状態で渡されます。"
    "確信が持てなくてもかまわないので、現時点で最も可能性が高いと思う解答を"
    "単語・フレーズだけで1つ、必ず答えてください。"
    "「わかりません」「PASS」のような回答は禁止です。説明や前置きも不要です。"
)

# LLM_PROVIDER の別名。どれを書いても同じプロバイダになります。
_PROVIDER_ALIASES = {
    "openai": "openai",
    "gpt": "openai",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "gemini": "gemini",
    "google": "gemini",
}

# プロバイダごとのデフォルトモデル。LLM_MODEL を空にするとこれを使います。
_DEFAULT_MODELS = {
    "openai": "gpt-5.6",
    "anthropic": "claude-sonnet-5",
    "gemini": "gemini-3.6-flash",
}

_openai_client = None
_anthropic_client = None
_gemini_client = None


def _provider() -> str:
    raw = (os.getenv("LLM_PROVIDER") or "openai").strip().lower()
    provider = _PROVIDER_ALIASES.get(raw)
    if provider is None:
        raise ValueError(
            f"未対応の LLM_PROVIDER です: {raw!r}\n"
            "openai / anthropic / gemini のいずれかを .env に設定してください。"
        )
    return provider


def _model(provider: str) -> str:
    return (os.getenv("LLM_MODEL") or "").strip() or _DEFAULT_MODELS[provider]


def _call_openai(partial_question: str) -> str:
    global _openai_client
    from openai import OpenAI

    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY が .env に設定されていません。")
        _openai_client = OpenAI(api_key=api_key)

    extra_params = {}
    reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", "none")
    if reasoning_effort:
        extra_params["reasoning_effort"] = reasoning_effort

    response = _openai_client.chat.completions.create(
        model=_model("openai"),
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": partial_question},
        ],
        **extra_params,
    )
    return (response.choices[0].message.content or "").strip()


def _call_anthropic(partial_question: str) -> str:
    global _anthropic_client
    from anthropic import Anthropic

    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません。")
        _anthropic_client = Anthropic(api_key=api_key)

    response = _anthropic_client.messages.create(
        model=_model("anthropic"),
        max_tokens=64,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": partial_question}],
    )
    texts = [block.text for block in response.content if getattr(block, "text", None)]
    return "".join(texts).strip()


def _call_gemini(partial_question: str) -> str:
    global _gemini_client
    from google import genai

    if _gemini_client is None:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY が .env に設定されていません。")
        _gemini_client = genai.Client(api_key=api_key)

    response = _gemini_client.models.generate_content(
        model=_model("gemini"),
        contents=partial_question,
        config={
            "system_instruction": _SYSTEM_PROMPT,
        },
    )
    return (response.text or "").strip()


def predict_answer(partial_question: str) -> Optional[str]:
    """
    Args:
        partial_question: これまでに読み上げられた問題文の断片。

    Returns:
        その時点で最も可能性が高いと思う解答(常に何か返します)。
    """
    provider = _provider()
    if provider == "openai":
        return _call_openai(partial_question)
    if provider == "anthropic":
        return _call_anthropic(partial_question)
    return _call_gemini(partial_question)
