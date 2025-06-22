# dbf-utils

CSV や DBF ファイルを正規化した SQLite データベースへ変換するためのツール集です。
`pandas` と `dbfread` が必要となります。開発環境では次のようにインストールしてください。

```bash
pip install -e .
```

## ディレクトリ構成

- `src/dbf_utils/` - 汎用ライブラリ本体
- `src/dbf_utils/r2ka/` - e-Stat R2KA 向けモジュール
- `app/` - 汎用スクリプト
- `app/estat/` - e-Stat 用スクリプト
- `doc/estat/` - e-Stat 用ドキュメント
- `tests/estat/` - e-Stat 用テストコード
- `dev/` - 開発用ファイル
- `sample/` - サンプルスクリプト

### 主なスクリプト

- `app/build_database.py` - 任意の CSV 群を 1 つのデータベースにまとめます。
- `app/import_generic_dbf.py` - 単一の DBF を簡易的に取り込むサンプル。
- `app/estat/import_r2ka.py` - `doc/estat/R2KA_database_spec.md` のスキーマに従って R2KA 形式の CSV/DBF を取り込みます。
- `app/import_n03.py` - 国土数値情報 N03 形式の DBF を取り込みます。

## 使用例

### 汎用 CSV 取り込み

```bash
python app/build_database.py CSVディレクトリ 出力.db
```

### 汎用 DBF 取り込み

```bash
python app/import_generic_dbf.py 出力.db data.dbf
```

### N03 DBF 取り込み

```bash
python app/import_n03.py 出力.db dev/N03-20240101_33.dbf
```

### R2KA CSV/DBF の取り込み

```bash
python app/estat/import_r2ka.py 出力.db ./data/*.{csv,dbf}
```

`--encoding` オプションでファイルの文字コードを指定できます。既定値は `cp932` です。

## テスト実行

```bash
pytest
```

`dev/r2ka11.dbf` を用いた統合テストが実行されます。
