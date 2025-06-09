# Estat SHP Utils

CSV ファイルを正規化した形で SQLite データベースへ変換するためのツール集です。
`pandas` と `dbfread` が必要となります。

## ディレクトリ構成


- `src/` - 汎用ライブラリ
- `app/` - コマンドラインスクリプト
- `dev/` - 開発用ファイル
- `doc/` - ドキュメント

### 主なスクリプト

- `app/build_database.py` - 任意の CSV 群を 1 つのデータベースにまとめます。
- `app/import_r2ka.py` - `doc/R2KA_database_spec.md` のスキーマに従って R2KA 形式の CSV/DBF を取り込みます。

## 使用例

### 汎用 CSV 取り込み

```bash
python app/build_database.py CSVディレクトリ 出力.db
```

### R2KA CSV/DBF の取り込み

```bash
python app/import_r2ka.py 出力.db ./data/*.{csv,dbf}
```

