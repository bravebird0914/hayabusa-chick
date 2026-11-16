"""push! 規約。

戻り値の先頭がちょうど ``push!`` なら、その呼び出しで押したとみなす。
続く文字列が解答。大文字小文字や全角には直さない。

hayabusa-chick と hayabusa-cup で、このファイルの parse_output は同じにする。
"""

PUSH_MARK = "push!"


def parse_output(raw: str | None) -> tuple[bool, str]:
    """Returns:
        (押したか, 解答または途中の考え)
        押していないときは、表示用に前後の空白だけ除いた文字列。
    """
    if not isinstance(raw, str):
        return False, ""
    if raw.startswith(PUSH_MARK):
        return True, raw[len(PUSH_MARK) :].strip()
    return False, raw.strip()
