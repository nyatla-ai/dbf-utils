# CSV から SQLite への変換

複数の CSV ファイルを正規化した SQLite データベースに変換する手順をまとめています。処理を行うモジュールは `src` ディレクトリにあり、`app` 配下のスクリプトから利用できます。

## 使い方

```bash
python app/build_database.py CSVディレクトリ 出力先.db
```

指定したディレクトリ内の `*.csv` を読み込み、共通する列を抽出してルックアップテーブルを生成しながら SQLite データベースを作成します。

### R2KA CSV を取り込む場合

```bash
python app/import_r2ka.py 出力.db ./data/*.csv
```

CSV は SJIS (cp932) でエンコードされている想定です。処理後、データベース内には UTF-8 として保存されます。
