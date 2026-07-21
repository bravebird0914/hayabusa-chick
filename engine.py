"""
hayabusa-chick: 実行エンジン

問題文をBPEトークン単位で1トークンずつ少しずつ読み上げるように表示し(逐次入力)、
そのたびに agent.predict_answer() を呼び出して、その時点での回答を
「入力に対する回答」として表示します。正解かどうかの自動判定は行いません。

このファイルは基本的に改造不要です。
挙動を変えたい場合は agent.py を編集してください。
"""

import csv
import time
from typing import List

import tiktoken

from agent import predict_answer

# 問題文をトークン化するエンコーディング(OpenAIのBPEトークナイザー)
_ENCODING = tiktoken.get_encoding("o200k_base")

# 1トークンを表示してから次のトークンを表示するまでの待機時間(秒)
REVEAL_DELAY_SECONDS = 0.1


def _tokenize(question_text: str) -> List[int]:
    return _ENCODING.encode(question_text)


def run(csv_path: str) -> None:
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        print(f"\n--- 問題 {row['No']} ---")
        token_ids = _tokenize(row["問題文"])

        for i in range(1, len(token_ids) + 1):
            partial_question = _ENCODING.decode(token_ids[:i])
            print(f"逐次入力: {partial_question}")

            answer = predict_answer(partial_question)
            print(f"入力に対する回答: {answer if answer else ''}")

            time.sleep(REVEAL_DELAY_SECONDS)
