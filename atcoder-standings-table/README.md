# atcoder-standings-table

このリポジトリは[AtCoder](https://atcoder.jp/)の特定のコンテストにおいて、特定の所属団体に属するメンバーだけをランキングとして表示するhtmlファイルを作成するためものです。

所属先のメンバーでAtCoderのコンテストに参加し、メンバー同士のみで競うことで技術（コーディング等）に対するモチベーションを上げたいという背景から作成しました。

一部、スクレイピングによってデータを取得する箇所があります。（悪用厳禁でお願いします。一切責任は負いませんのであらかじめご了承ください。）

## 実行環境

下記環境にて動作確認済みです。

- OS：Linux (Windows Subsystem for Linux 2)
  - Ubuntu 20.04.4 LTS
- 言語：Python 3.9.7
  - インストールが必要なライブラリ
    - pwinput
    - requests
    - urllib3
    - beautifulsoup4

## 実行例

```sh
$ git clone https://github.com/k0j1r0n0/misc.git
$ mv misc/atcoder-standings-table
$ python create_standings_html.py
```

- 実行時、下記パラメータを入力する必要があります。
  - `Username`：AtCoderアカウントのユーザ名
  - `Password`：AtCoderアカウントのパスワード
  - `Contest ID`：コンテストのID
    - AtCoder Beginner Contest 123の場合、コンテストのURL`https://atcoder.jp/contests/abc123`のうち`abc123`がIDとなります。
  - `Affiliation`：コンテスト登録時の所属団体名

- コンソール画面の出力例は下記の通りです。
  ```
  [Enter login information]
    Username: abcd1234
    Password: **********
  Successfully logged in to Atcoder!
  --------------------------------------------------
  [Enter the following basic information]
    Contest ID: abc123
    Affiliation: XXX corp.
  Generating files...
  --------------------------------------------------
  [Output]
    (1) ./html/abc123.html
    (2) ./json/abc123.json
  Done.
  ```

- 実行後、ディレクトリ`html`直下にできたhtmlファイルをブラウザ（例：Google Chrome）から開くことでランキング表を確認できます。