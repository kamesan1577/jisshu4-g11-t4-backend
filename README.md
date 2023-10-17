# Hate Abate

## 概要

ツイート中の不適切な発言を検出し、修正する Chrome 拡張機能のバックエンドです。

浪川：読み手側が不快にならない検出用と置き換えののモジュールを用意します。

# 環境構築 (筆者は Ubuntu 22.04 を使用)

1. 仮想環境の作成
   <br>
   Ubuntu
   ```bash
   python3 -m venv venv
   ```
   Windows
   ```powershell
   python -m venv venv
   ```
2. 仮想環境の有効化
   <br>
   Ubuntu
   ```bash
   source venv/bin/activate
   ```
   Windows
   ```powershell
   .\venv\Scripts\activate
   ```
3. 依存パッケージのインストール
   <br>
   共通
   ```bash
   pip install -r requirements.txt
   ```
4. サーバーの起動
   <br>
   共通
   ```bash
   uvicorn src.main:app --reload
   ```
5. ブラウザで http://localhost:8000/docs にアクセス
   <br>
   API の仕様書が表示されれば成功です。
# 参考
- https://developer.yahoo.co.jp/webapi/jlp/ma/v2/parse.html
- http://monoroch.net/kinshi/
