# Word2Vec を用いた加減算単語当てゲーム

大学院の自然言語処理に関する講義の最終課題で作成したオリジナルアプリケーションです．
初めて作成した Web アプリケーションなのでいろいろ修正ポイントなどがありますが，現状動くものをアップロードしています．

## 技術要素

- フロント：HTML，CSS（Bootstrap4），Javascript（jQuery）
- サーバサイド：Python3 (Flask)
- Word2Vec の学習 : Gensim

## 実行環境

### データ準備

[こちら](/app/data/README.md)を参照して、 Word2Vec のモデルファイルをダウンロードしてきてください。

### ローカル環境

実行に必要な Python のモジュールなどは requirements.txt にまとめていますので，参照していただければ幸いです．
モジュールなどのインストールが終わった方は[実行手順](#operation)に従って実行してください．

<h4 id='operation'>実行手順</h2>

- python webserver.py でサーバ起動
- localhost:8888 に接続

### Docker Compose で立ち上げる

docker や docker-compose のインストールに関しては[Get Docker](https://docs.docker.com/get-docker/)を参照ください．
MacOS の場合は`Docker Desktop on Mac`を入れた段階で `docker compose` も同時に使うことができます．Linux をご利用の方は追加でインストールが必要かと思いますので，[Install Docker Compose](https://docs.docker.com/compose/install/)を参考にインストールしてください．

```sh
$ docker compose build --no-cache
$ docker compose up -d

# ログは以下のコマンドで確認できます
$ docker compose logs -f

```

---

## アプリケーション概要

このアプリケーションは，Word2Vec の特徴である「単語間の加減算ができる」という点に着目したゲームです．

具体的には Word2Vec は単語をベクトル空間上で表現することで単語間の意味関係を表現します．そのため，有名な例として`日本 - 東京 + パリ = フランス`といった単語の加減算ができます．
このような特徴を活かして，問題として与えられる 2 単語の加減算単語を当てましょうというゲームとなっています．
先ほどの例（`日本 - 東京 + パリ = フランス`）で説明すると，日本（開始単語）とフランス（目標単語）の 2 単語がもし与えられた場合，その加減算単語`「- 東京」と「+ パリ」`を当てる（考える）といったゲームとなります．

さらに，今回はアプリケーションに対して以下の理由からいくつか制約を与えています．

- ランダムに 2 単語生成するとその単語間の関係性がほとんど無く，ゲームとして成り立たない
  - 開始単語のみランダムに生成し，開始単語に類似した単語を目標単語として選定する
  - 類似度の閾値として類似度の高さが 6 番目から 15 番目の中から選定する（6 番目からとしている理由は[ルール](#rule)を参照してください．）
- 全く知らない単語が出てくるとその加減算単語を当てにくく，ゴールへ遠ざかる
  - 分からない単語があるとその意味を調べるはずなので，Wikipedia の結果をあらかじめヒントとして与える

<h2 id='rule'>ルール</h2>

#### **スタート単語からゴール単語までどのような単語で加減算を行えばいいか 10 手以内に求める．**

- Word2Vec の学習で構築した語彙の中からランダムでスタート単語が決定されます．
- 難易度が高すぎたため，スタート単語との類似度が上位 6 位から 15 位までの単語をゴール単語としてランダム選択しています．
- 加減算が行われた段階で現段階の類似度ランキングが表で出力されます．ランダムで出題されるため難しい単語があった場合のために WikipediaAPI を用いて概要を抜き出したものがボタンを押すことで見ることができます．
- 1 タームごとのクリア条件は，計算結果の単語が類似度ランキングで上位 5 位以内に入ることです．

まとめると，クリア条件は 10 手以内に開始単語に加減算を行い，目標単語の類似度順位が上位 5 位以内に入ることです．

<!-- # 問題点と改善点（現状）
- もし的外れな単語を加減算してしまうと目標単語までの類似度の順位が下がってしまい，今の現状が分からなくなるためクリアできなくなってしまう
    - 類似度ランキングの表だけでなく，目標単語の順位も常に出力する
- モダンな技術に置き換える
- pythonファイルの細かな設定変更
-->
