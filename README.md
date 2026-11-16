# hayabusa-chick

早押しクイズエージェント作成用の最小構成テンプレートです。

問題文をBPEトークン(`tiktoken`)単位で1トークンずつ少しずつ読み上げるように表示し、そのたびにあなたのエージェント(`agent.py`)を呼び出します。押すタイミングはエージェントが自分で決めます。押すときは、戻り値の先頭を `push!` にして解答を返してください。`push!` が出たトークン位置が、その問題の押しポイントです。

```python
return "push! ナポレオン"
```

`push!` が付いていない戻り値は「まだ押していない考え」として表示されるだけで、押したことにはなりません。問題文は `push!` が出るまで読み上げられ、最後まで出なければ「スルー」です。手元での実行では、正答との簡易照合も表示します。大会での正式な正誤は、運営が別途判定します。

## 動作環境

Windows・macOS・Linuxのいずれでも動作します。Python 3.10以降が必要です。

## セットアップ

このセクションの手順を上から順番に実行すれば準備は完了します。コマンドはそのままコピペして実行できます。

### 0. 事前に必要なもの

- **Git**: ターミナルで `git --version` と入力してバージョンが表示されればOKです。表示されない場合は [Git公式サイト](https://git-scm.com/downloads) からインストールしてください。
- **Python 3.10以上**: ターミナルで `python3 --version`(Windowsの場合は `python --version`)と入力してバージョンが表示されればOKです。表示されない、またはバージョンが古い場合は [Python公式サイト](https://www.python.org/downloads/) からインストールしてください。

### 1. リポジトリを取得する

```bash
git clone git@github.com:bravebird0914/hayabusa-chick.git
cd hayabusa-chick
```

> SSHキーを設定していない場合は、代わりに次のコマンドを使ってください。
>
> ```bash
> git clone https://github.com/bravebird0914/hayabusa-chick.git
> cd hayabusa-chick
> ```

### 2. Python環境を準備する

自分が使っているOSに合うブロックを1つ選んで、そのままコピペで実行してください(仮想環境の作成・有効化・ライブラリのインストール・`.env`ファイルの準備までまとめて行われます)。

**macOS / Linux の場合**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows の場合(コマンドプロンプト)**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**Windows の場合(PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

実行後、ターミナルの行頭に `(.venv)` と表示されていれば仮想環境が有効になっています。

### 3. 使うLLMとAPIキーを設定する

作成された `.env` ファイルをテキストエディタ(メモ帳・VS Codeなど何でもOK)で開き、次の2つだけ設定してください。

**1. 使うプロバイダを1行で指定する**

```
LLM_PROVIDER=openai
```

`openai` / `anthropic` / `gemini` のいずれかを書いてください(`gpt` / `claude` / `google` でも同じ意味です)。

**2. そのプロバイダのAPIキー行の先頭の `#` を消して、キーを貼り付ける**

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

| プロバイダ | `.env` に書く値 | APIキーの変数名 | キーの取得先 |
| --- | --- | --- | --- |
| OpenAI (GPT) | `openai` または `gpt` | `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com/api-keys) |
| Anthropic (Claude) | `anthropic` または `claude` | `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com/settings/keys) |
| Google (Gemini) | `gemini` または `google` | `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |

切り替えたいときは、`LLM_PROVIDER` の値を変えて、対応するAPIキーを入れてから、もう一度 `./run.sh` を実行するだけです。コードを書き換える必要はありません。

### 4. 動作確認

**macOS / Linux の場合**

```bash
./run.sh
```

**Windows の場合**

```bat
run.bat
```

問題文が少しずつ画面に表示され、各トークンごとに回答が出ればセットアップは成功です。

> `run.sh` / `run.bat` は、セットアップ(仮想環境の作成・ライブラリのインストール・`.env`の作成)が終わっていない場合は自動で行い、終わっていれば実行だけを行う、実行用のショートカットスクリプトです。中身は `python main.py data/sample_questions.csv` を実行しているだけです。
>
> `./run.sh` で `Permission denied` と表示された場合は、`chmod +x run.sh` を実行してから、もう一度お試しください。

### うまくいかないときは

| 症状 | 対処法 |
| --- | --- |
| `python3: command not found` や `python: command not found` と出る | Pythonが未インストール、またはPATHが通っていません。[Python公式サイト](https://www.python.org/downloads/) から入れ直してください。 |
| `activate` を実行しても `(.venv)` が表示されない | OSに合ったコマンドを使っているか確認してください(上記の3つのブロックはOSごとに内容が異なります)。 |
| PowerShellで `.venv\Scripts\Activate.ps1` がエラーになる(実行ポリシー関連) | PowerShellを管理者権限で開き、`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` を実行してから、もう一度お試しください。 |
| `pip install -r requirements.txt` でエラーになる | 先に `python -m pip install --upgrade pip` を実行してpipを最新化してから、もう一度お試しください。 |
| 次回以降、ターミナルを開き直したら動かない | 仮想環境は毎回有効化が必要です。`hayabusa-chick` フォルダで、手順2の「有効化」コマンド(2行目)だけ再実行してください。 |

## 実行方法

**macOS / Linux の場合**

```bash
./run.sh
```

**Windows の場合**

```bat
run.bat
```

自分で用意したCSVファイルを使いたい場合は、引数でパスを渡してください。

```bash
./run.sh data/your_questions.csv
```

```bat
run.bat data\your_questions.csv
```

(仮想環境をすでに有効化していて、直接Pythonコマンドで実行したい場合は `python main.py data/sample_questions.csv` でも同様に実行できます。)

同梱している `data/sample_questions.csv` には、動作確認用として「勝抜杯2022」の1問目のみを収録しています(他の問題データはこのリポジトリには含まれていません)。

## push! の規約

`predict_answer(partial_question)` の戻り値は文字列です。

| 戻り値 | 意味 |
| --- | --- |
| `push! ナポレオン` | このトークンで押した。解答は「ナポレオン」 |
| `push!` | 押したが解答が空。無回答（誤答扱い） |
| `ナポレオン` | まだ押していない。画面には考えとして出る |
| `Push!` や `ｐｕｓｈ！` | 押したことにはならない（`push!` ちょうど一致のみ） |

いつ `push!` を出すかは、エージェントを書く人に任されています。運営から押し方は指定しません。

同梱の `agent.py` は叩き台です。LLM に解答だけを言わせ、**同じ解答が 3 回続いたら `push!`** します。回数は `.env` の `PUSH_STREAK` で変えられます。

## 改造のヒント

- 確信度がしきい値を超えたときだけ `push!` する
- 問題文の続きを予測してから、足りない情報があるうちは押さない
- 固有名詞や年号が出るまでは考えだけ返し、決め手が出てから押す
- 早い位置で押すほど速いが、誤答になる。遅いと正確でも負ける

大会の実行環境は、このリポジトリの `engine.py` ではなく運営側のハーネスが `predict_answer()` を呼びます。解釈は `protocol.py` の `parse_output()` と同じです。手元で動いた押し方が、本番でも同じ位置になります。

## API

- サンプル実装は OpenAI / Anthropic / Gemini に対応しています。`.env` の `LLM_PROVIDER` を書き換えるだけで切り替えられます。
- APIキーは `.env` に設定し、`os.getenv("YOUR_API_KEY")` のように読み込んでください。
- 接続先をプロキシなどに変えるときは `OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` / `GEMINI_BASE_URL` を設定します。クライアントはこれらの値を使います。
- `predict_answer()` は問題文の 1 トークンごとに毎回呼び出されます。`push!` を返すとその問題は終わりです。

### プロバイダの切り替え

`.env` のこの1行だけを変えます。

```
LLM_PROVIDER=openai
```

```
LLM_PROVIDER=anthropic
```

```
LLM_PROVIDER=gemini
```

### モデルの変更

モデル名はコードを書き換えなくても `.env` で変更できます。空なら各プロバイダのデフォルトを使います。

| プロバイダ | デフォルトモデル | 変更例 |
| --- | --- | --- |
| openai | `gpt-5.6` | `LLM_MODEL=gpt-4o` |
| anthropic | `claude-sonnet-5` | `LLM_MODEL=claude-haiku-4-5` |
| gemini | `gemini-3.6-flash` | `LLM_MODEL=gemini-2.5-pro` |

```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
# GPT-5系以外のモデルを使う場合は、次を空にして reasoning_effort を無効化してください
OPENAI_REASONING_EFFORT=
```

ローカルLLMなど、上記3つ以外を使いたい場合は `agent.py` の `predict_answer()` を書き換えてください。

## CSVフォーマット

```csv
No,問題文,解答
1,問題文の本文,正答
```

## 今後の予定

叩き台（このリポジトリ）は改良を続けます。押し方の例を増やしたり、練習用の表示を分かりやすくしたりします。複数エージェントの対戦そのものは、運営側の競技場でログを再生して行います。参加者のプログラムが対戦相手のコードを直接呼ぶことはありません。
