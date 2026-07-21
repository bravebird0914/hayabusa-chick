@echo off
setlocal

rem ================================================================
rem   hayabusa-chick 実行スクリプト (Windows 用)
rem
rem   使い方:
rem     run.bat                          サンプル問題で実行
rem     run.bat data\your_questions.csv  指定したCSVで実行
rem ================================================================

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "CSV_PATH=%~1"
if "%CSV_PATH%"=="" set "CSV_PATH=data\sample_questions.csv"

if not exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    echo [初回セットアップ] 仮想環境を作成します...
    python -m venv .venv
)

call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

python -c "import openai, dotenv, tiktoken" >nul 2>&1
if errorlevel 1 (
    echo [初回セットアップ] 必要なライブラリをインストールします...
    pip install -q -r requirements.txt
)

if not exist "%SCRIPT_DIR%.env" (
    copy "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >nul
    echo.
    echo [警告] .env を作成しました。APIキーが未設定です。
    echo        .env を開いて、使いたいLLMプロバイダのAPIキーを記入してから、もう一度 run.bat を実行してください。
    exit /b 1
)

if not exist "%CSV_PATH%" (
    echo [エラー] CSVファイルが見つかりません: %CSV_PATH%
    exit /b 1
)

echo %CSV_PATH% を実行します...
echo.
python main.py "%CSV_PATH%"
