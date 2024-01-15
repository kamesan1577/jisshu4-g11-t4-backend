# へいたん
フロントエンド→https://github.com/kamesan1577/jisshu4-g11-t4-frontend
## 概要

ツイート中の不適切な発言を検出し、修正する Chrome 拡張機能のバックエンドです。
<br>
フレームワークにはFastAPIを使用しており、[/docs](https://0htjwvzstd.execute-api.ap-northeast-1.amazonaws.com/master/docs) にアクセスすることでSwaggerによって自動生成されたOpenAPI Documentを参照できます
<br>
インフラはAWS Lambdaを軸に、キャッシュサーバーとしてRedisを用いています。(デプロイ環境では[upstash](https://upstash.com/)を利用)

## 構成
![jisshuGraph](https://github.com/kamesan1577/jisshu4-g11-t4-backend/assets/47214420/1a11810c-aec5-44d1-b92a-7b71b4e2ee79)

# 参考

- https://developer.yahoo.co.jp/webapi/jlp/ma/v2/parse.html
- http://monoroch.net/kinshi/
