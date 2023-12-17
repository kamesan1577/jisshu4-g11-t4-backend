# Hate Abate

## 概要

ツイート中の不適切な発言を検出し、修正する Chrome 拡張機能のバックエンドです。
<br>
フレームワークにはFastAPIを使用しており、[/docs](https://0htjwvzstd.execute-api.ap-northeast-1.amazonaws.com/master/docs) にアクセスすることでSwaggerによって自動生成されたOpenAPI Documentを参照できます
<br>
インフラはAWS Lambdaを軸に、キャッシュサーバーとしてRedisを用いています。(デプロイ環境では[upstash](https://upstash.com/)を利用)
<br>
浪川：読み手側が不快にならない検出用と置き換えのモジュールを用意します。

# 環境構築 (Ubuntu 22.04,Python3.10を利用)

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
4. 環境変数の設定
   Ubuntu
   ```bash
   cp .env.sample .env
   ```
   作成された.envファイルに必要な情報を書き込む
   <br>
   <br>
   Windows
   ```powershell
   Windowsの人は.env.sampleを参考にして頑張って設定してください
   ```
6. サーバーの起動
   <br>
   共通
   ```bash
   uvicorn src.main:app --reload
   ```
7. ブラウザで http://localhost:8000/docs にアクセス
   <br>
   API の仕様書が表示されれば成功です。
# 参考
- https://developer.yahoo.co.jp/webapi/jlp/ma/v2/parse.html
- http://monoroch.net/kinshi/
