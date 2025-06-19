# CSV から SQLite への変換

複数の CSV ファイルを正規化した SQLite データベースに変換する手順をまとめています。処理を行うモジュールは `src` ディレクトリにあり、`app` 配下のスクリプトから利用できます。
`pandas` と `dbfread` のインストールが必要です。

## 使い方

```bash
python app/build_database.py CSVディレクトリ 出力先.db
```

指定したディレクトリ内の `*.csv` を読み込み、共通する列を抽出してルックアップテーブルを生成しながら SQLite データベースを作成します。

### R2KA CSV/DBF を取り込む場合

```bash
python app/import_r2ka.py 出力.db ./data/*.{csv,dbf}
```

`--encoding` オプションで CSV/DBF ファイルの文字コードを指定可能です。既定値は
`cp932` となります。

CSV 内に登録できないレコードが見つかった場合、その行を表示して処理を終了します。

CSV は SJIS (cp932) でエンコードされている想定です。処理後、データベース内には UTF-8 として保存されます。
