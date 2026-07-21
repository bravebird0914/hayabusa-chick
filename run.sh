#!/bin/bash
# ================================================================
# hayabusa-chick 実行スクリプト (macOS / Linux 用)
#
#  使い方:
#    ./run.sh                          # サンプル問題で実行
#    ./run.sh data/your_questions.csv  # 指定したCSVで実行
# ================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

CSV_PATH="${1:-data/sample_questions.csv}"

# ── セットアップが未完了なら自動で行う ──────────────────────────
if [ ! -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    echo "🔧 初回セットアップ: 仮想環境を作成します..."
    python3 -m venv .venv
fi

source "$SCRIPT_DIR/.venv/bin/activate"

if ! python -c "import openai, dotenv, tiktoken" >/dev/null 2>&1; then
    echo "🔧 初回セットアップ: 必要なライブラリをインストールします..."
    pip install -q -r requirements.txt
fi

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo ""
    echo "   .env を作成しました。APIキーが未設定です。"
    echo "   .env を開いて、使いたいLLMプロバイダのAPIキーを記入してから、もう一度 ./run.sh を実行してください。"
    exit 1
fi

if [ ! -f "$CSV_PATH" ]; then
    echo "CSVファイルが見つかりません: $CSV_PATH"
    exit 1
fi

echo "▶ $CSV_PATH を実行します..."
echo ""
python main.py "$CSV_PATH"
