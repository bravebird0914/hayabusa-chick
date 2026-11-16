"""
hayabusa-chick: 実行エンジン

問題文を BPE トークン単位で 1 トークンずつ表示し、そのたびに
agent.predict_answer() を呼び出します。戻り値が push! で始まった時点で
その問題を打ち切り、押した位置と解答を表示します。

このファイルは基本的に改造不要です。
挙動を変えたい場合は agent.py を編集してください。
"""

import csv
import re
import sys
import time
import unicodedata
from typing import Callable, List, Optional

import tiktoken

from protocol import parse_output

# 問題文をトークン化するエンコーディング（本番ハーネスと同じ）
_ENCODING = tiktoken.get_encoding("o200k_base")

# 1トークンを表示してから次のトークンを表示するまでの待機時間（秒）
REVEAL_DELAY_SECONDS = 0.1


def _tokenize(question_text: str) -> List[int]:
    return _ENCODING.encode(question_text)


def _paint(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"\s+", "", text)
    return text.casefold()


def _practice_verdict(answer: str, gold: str) -> str:
    """手元練習用の照合。大会の正式判定は運営側で行う。"""
    if not _norm(answer):
        return "無回答（誤答扱い）"
    options = re.split(r"[／/]", gold or "")
    if any(_norm(answer) == _norm(option) for option in options if option.strip()):
        return "正解（簡易照合）"
    return "不一致（簡易照合。最終判定は運営）"


def _announce_push(token_pos: int, total: int, answer: str, gold: str) -> None:
    verdict = _practice_verdict(answer, gold)
    bar = "=" * 44
    print()
    print(_paint(bar, "93"))
    print(_paint(f"  push!   {token_pos}/{total} トークン", "1;93"))
    print(_paint(f"  解答: {answer if answer else '（空）'}", "93"))
    color = "92" if verdict.startswith("正解") else "91"
    print(_paint(f"  照合: {verdict}", color))
    print(_paint(bar, "93"))
    print()


def run(
    csv_path: str,
    predict: Optional[Callable[[str], str]] = None,
    sleep_seconds: Optional[float] = None,
) -> None:
    if predict is None:
        from agent import predict_answer as predict

    delay = REVEAL_DELAY_SECONDS if sleep_seconds is None else sleep_seconds

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        print(f"\n--- 問題 {row['No']} ---")
        token_ids = _tokenize(row["問題文"])
        total = len(token_ids)
        gold = row.get("解答", "")

        pushed = False
        for i in range(1, total + 1):
            partial_question = _ENCODING.decode(token_ids[:i])
            print(f"逐次入力: {partial_question}")

            try:
                raw = predict(partial_question)
            except Exception as exc:
                print(f"入力に対する回答: （エラー: {exc}）")
                time.sleep(delay)
                continue

            is_push, text = parse_output(raw if isinstance(raw, str) else "")
            if is_push:
                _announce_push(i, total, text, gold)
                pushed = True
                break

            print(f"入力に対する回答: {text}")
            time.sleep(delay)

        if not pushed:
            print(_paint("スルー（最後まで push! なし）", "90"))
