# Mental Support AI

## 概要
うつ病の方向けに福祉サービスを提案するAIチャットボット

## デモ
![demo](./docs/demo.png)

## 特徴
- 会話形式で状態整理
- 福祉制度を自動判定（ルールベース）
- 地域別に窓口を提示
- Web / LINE対応

## 技術スタック
- Python（Flask）
- LINE Messaging API
- JSONベースDB
- スコアリングロジック

## ディレクトリ構成
```bash
app.py         # Webサーバー
line_bot.py    # LINE Bot処理
services.py    # ロジック（中核）
data/          # 地域・制度データ
templates/     # HTML
