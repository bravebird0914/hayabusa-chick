"""
hayabusa-chick: 早押しクイズエージェント（叩き台）

改造するのはこのファイルだけです。

predict_answer() は、問題文が少しずつ読み上げられるたびに呼び出されます。
押すときは、戻り値の先頭を push! にして、続けて解答を返してください。

    return "push! ナポレオン"

push! が付いていない戻り値は「まだ押していない考え」として表示されるだけで、
押したことにはなりません。いつ push! を出すかは、このファイルを書く人に任されています。

この叩き台は「同じ解答が PUSH_STREAK 回（既定は 3 回）続いたら押す」です。
使う LLM は .env の LLM_PROVIDER で切り替えます（openai / anthropic / gemini）。
モデル名は LLM_MODEL で変更できます。未設定なら各プロバイダのデフォルトを使います。
API の接続先を変えたいときは OPENAI_BASE_URL / ANTHROPIC_BASE_URL / GEMINI_BASE_URL を使います。
"""

import os
from typing import Optional

_SYSTEM_PROMPT = (
    "あなたは早押しクイズの回答者です。"
    "問題文はまだ最後まで読み終わっていない途中の状態で渡されます。"
    "確信が持てなくてもかまわないので、現時点で最も可能性が高いと思う解答を"
    "単語・フレーズだけで1つ、必ず答えてください。"
    "「わかりません」「PASS」のような回答は禁止です。説明や前置きも不要です。"
    "push! という文字列は出力しないでください。"
)

_PROVIDER_ALIASES = {
    "openai": "openai",
    "gpt": "openai",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "gemini": "gemini",
    "google": "gemini",
}

_DEFAULT_MODELS = {
    "openai": "gpt-5.6",
    "anthropic": "claude-sonnet-5",
    "gemini": "gemini-3.6-flash",
}

_openai_client = None
_anthropic_client = None
_gemini_client = None

_prev_partial: Optional[str] = None
_streak_answer: Optional[str] = None
_streak = 0


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


def _streak_needed() -> int:
    raw = (os.getenv("PUSH_STREAK") or "3").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 3
    return max(1, n)


def _call_openai(partial_question: str) -> str:
    global _openai_client
    from openai import OpenAI

    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY が .env に設定されていません。")
        kwargs = {"api_key": api_key}
        base_url = (os.getenv("OPENAI_BASE_URL") or "").strip()
        if base_url:
            kwargs["base_url"] = base_url
        _openai_client = OpenAI(**kwargs)

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
        kwargs = {"api_key": api_key}
        base_url = (os.getenv("ANTHROPIC_BASE_URL") or "").strip()
        if base_url:
            kwargs["base_url"] = base_url
        _anthropic_client = Anthropic(**kwargs)

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
        kwargs = {"api_key": api_key}
        base_url = (os.getenv("GEMINI_BASE_URL") or os.getenv("GOOGLE_API_BASE") or "").strip()
        if base_url:
            from google.genai import types

            kwargs["http_options"] = types.HttpOptions(base_url=base_url)
        _gemini_client = genai.Client(**kwargs)

    response = _gemini_client.models.generate_content(
        model=_model("gemini"),
        contents=partial_question,
        config={
            "system_instruction": _SYSTEM_PROMPT,
        },
    )
    return (response.text or "").strip()


def _guess(partial_question: str) -> str:
    provider = _provider()
    if provider == "openai":
        answer = _call_openai(partial_question)
    elif provider == "anthropic":
        answer = _call_anthropic(partial_question)
    else:
        answer = _call_gemini(partial_question)
    # モデルが規約語を返しても、押し判断はここ（叩き台）が行う。
    if answer.startswith("push!"):
        answer = answer[len("push!") :].strip()
    return answer


def predict_answer(partial_question: str) -> str:
    """
    Args:
        partial_question: これまでに読み上げられた問題文の断片。

    Returns:
        押すときは ``push! 解答``。押さないときは、その時点の考え。
    """
    global _prev_partial, _streak_answer, _streak

    if _prev_partial is not None and not partial_question.startswith(_prev_partial):
        _streak_answer = None
        _streak = 0
    _prev_partial = partial_question

    answer = _guess(partial_question)
    if answer and answer == _streak_answer:
        _streak += 1
    else:
        _streak_answer = answer
        _streak = 1 if answer else 0

    if answer and _streak >= _streak_needed():
        return f"push! {answer}"
    return answer
