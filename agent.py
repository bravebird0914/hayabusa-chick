"""
hayabusa-chick: 早押しクイズエージェント

改造するのはこのファイルだけです。

predict_answer() は、問題文が少しずつ読み上げられるたびに呼び出されます。
まだ問題文が最後まで読まれていなくても、確信が持てなくても構わないので、
その時点で最も可能性が高いと思う解答を常に1つ返してください。

好きなLLM API(OpenAI, Anthropic, Gemini, ローカルLLMなど)を自由に呼び出してください。
APIキーは .env に設定し、os.getenv("YOUR_API_KEY") のように読み込んでください。

このファイルはOpenAIを使った動作確認用のサンプル実装です。
回答が正解かどうかの自動判定は行いません。表示された回答が正しいかどうかは、
実行している人が自分の目で確認してください。
"""

import os
from typing import Optional

from openai import OpenAI

_client: Optional[OpenAI] = None

# 使用するモデルは .env で自由に変更できます(未設定なら gpt-5.6)。
# 例: OPENAI_MODEL=gpt-4o
_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")

# reasoning_effort は GPT-5 系のみ対応のパラメータです。
# GPT-5 以外のモデル(gpt-4o など)を使う場合は .env で OPENAI_REASONING_EFFORT= を
# 空にしておくと、このパラメータを送信しません。
_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "none")

_SYSTEM_PROMPT = (
    "あなたは早押しクイズの回答者です。"
    "問題文はまだ最後まで読み終わっていない途中の状態で渡されます。"
    "確信が持てなくてもかまわないので、現時点で最も可能性が高いと思う解答を"
    "単語・フレーズだけで1つ、必ず答えてください。"
    "「わかりません」「PASS」のような回答は禁止です。説明や前置きも不要です。"
)


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def predict_answer(partial_question: str) -> Optional[str]:
    """
    Args:
        partial_question: これまでに読み上げられた問題文の断片。

    Returns:
        その時点で最も可能性が高いと思う解答(常に何か返します)。
    """
    extra_params = {}
    if _REASONING_EFFORT:
        extra_params["reasoning_effort"] = _REASONING_EFFORT

    response = _get_client().chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": partial_question},
        ],
        **extra_params,
    )
    return (response.choices[0].message.content or "").strip()
