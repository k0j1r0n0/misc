# atcoder-standings-table

## 概要

このリポジトリは[AtCoder](https://atcoder.jp/)が主催のコンテストについて、選択したコンテストのうちある所属団体に属する参加者のみの情報を元にして、ランキングを作成するスクリプトを格納しています。出力されるファイルの形式は.jsonと.htmlです。

所属先のメンバーで[AtCoder](https://atcoder.jp/)のコンテストに参加し、メンバー同士のみで競うことで技術（コーディング等）に対するモチベーションを上げるきっかけにしたいという背景から作成しました。

一部、スクレイピングによってデータを取得する箇所があります。悪用厳禁でお願いします。一切責任は負いませんのであらかじめご了承ください。

スクリプトは次の表の通りです。
|スクリプト名|説明|
|--|--|
|[`generate_standings.py`](#generate_standingspy)|ある1つのコンテストについて、ある所属団体に所属する参加者だけを抜き出してランキングとして表示するスクリプト（コンテスト、所属団体はユーザによって選択）|
|[`generate_best_standings.py`](#generate_best_standingspy)|1つ以上のコンテストについてある所属団体に所属する参加者だけを抜き出し、その参加者の最高得点を元に1つのランキングとして表示するスクリプト（コンテスト、所属団体はユーザによって選択）|

**※事前にAtCoderアカウントを取得してください。（「順位表」のデータを取得するにはAtCoderにログインする必要があるため）**

## 実行環境

下記環境にて動作確認済みです。

- OS：Linux (Windows Subsystem for Linux 2)
  - Ubuntu 20.04.4 LTS
- 言語：Python 3.9.7

また、次のPythonライブラリはインストールが必要です。
- Pythonライブラリ（①：`generate_standings.py`、②：`generate_best_standings.py`）
  - pwinput（①、②）
  - requests（①、②）
  - urllib3（①、②）
  - beautifulsoup4（①）
  - pandas（②）

実行する前に下記のように手元の環境にクローンし、スクリプトのあるディレクトリに移動してください。
```sh
$ git clone https://github.com/k0j1r0n0/misc.git
$ mv misc/atcoder-standings-table
```
そして、ディレクトリ`html`、`json`があることを確認してください。

## 実行例

### generate_standings.py

- 実行時、下記パラメータを入力する必要があります。
  - `Username`：AtCoderアカウントのユーザ名
  - `Password`：AtCoderアカウントのパスワード
  - `Contest ID`：コンテストのID
    - AtCoder Beginner Contest 123の場合、コンテストのURL`https://atcoder.jp/contests/abc123`のうち`abc123`がIDとなります。
  - `Affiliation`：コンテスト登録時の所属団体名

- 実行例
  ```sh
  $ python generate_standings.py
  ```

- コンソール画面の例は下記の通りです。
  ```
  [Enter login information]
    Username: k0j1r0n0
    Password: ***************
  Successfully logged in to Atcoder!
  --------------------------------------------------
  [Enter the following basic information]
    Contest ID: abc123
    Affiliation: "XXX Univ."
  Generating files...
  --------------------------------------------------
  [Output]
    (1) ./html/abc123.html
    (2) ./json/abc123.json
  Done.
  ```

- 実行後、ディレクトリ`html`直下にできたhtmlファイルをGoogle Chrome等のブラウザから開くことでランキング表を確認できます。

### generate_best_standings.py

- 実行時、下記パラメータを入力する必要があります。
  - `Username`：AtCoderアカウントのユーザ名
  - `Password`：AtCoderアカウントのパスワード
  - `Contest ID`：コンテストのID（generate_standings.pyと同様）
    - スペース区切りで複数入力が可能。（例：`abc123` `abc111` `arc101`）
  - `Affiliation`：コンテスト登録時の所属団体名
- 引数にあらかじめ指定する場合としない場合の2つが選べます。
  - **引数に指定する場合**
    ```sh
    $ mv misc/atcoder-standings-table
    $ python generate_best_standings.py -u k0j1r0n0 -a "XXX株式会社" -c abc123 abc111 arc101 -t "XYZ部主催 競技プログラミングコンテスト"
    ```
    - コンソール画面の例
      ```
      [Enter login information]
        Username: k0j1r0n0
        Password: ***************
      Successfully logged in to Atcoder!
      --------------------------------------------------
      [Enter the following basic information]
        Contest ID: abc123 abc111 arc101
        Affiliation: XXX株式会社
      Retrieving standings data from "https://atcoder.jp/contests/abc123/standings/json"...
      Retrieving standings data from "https://atcoder.jp/contests/abc111/standings/json"...
      Retrieving standings data from "https://atcoder.jp/contests/arc101/standings/json"...
      Generating json and html files...
      --------------------------------------------------
      [Output]
        - ./json/abc123_filtered.json
        - ./json/abc111_filtered.json
        - ./json/arc101_filtered.json
        - ./json/best_standings.json
        - ./html/best_standings.html
      Done.
      ```
  - **引数に指定しない場合**
    ```sh
    $ python generate_best_standings.py
    ```
    - コンソール画面の例
      ```
      [Enter login information]
        Username: k0j1r0n0
        Password: ***************
      Successfully logged in to Atcoder!
      --------------------------------------------------
      [Enter the following basic information]
        Contest ID: abc123 abc111 arc101
        Affiliation: XXX大学
      (以下、省略)
      ```