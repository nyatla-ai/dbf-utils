# R2KA データベース仕様

このドキュメントでは、`dev/r2ka11.dbf` に含まれる R2KA シェープファイルの属性データを正規化して格納するためのスキーマを説明します。

このデータセットは埼玉県内の行政区域ポリゴンを含みます。主な項目は以下のとおりです。

- `KEY_CODE` (C,11) – 下記コードを連結した一意の識別子
  （ソースデータにのみ存在し、正規化後のスキーマでは使用しません）
- `PREF` (C,2) – 都道府県コード
- `CITY` (C,3) – 市区町村コード
- `S_AREA` (C,6) – 市区町村内の小地域コード
- `PREF_NAME` (C,12) – 都道府県名
- `CITY_NAME` (C,16) – 市区町村名
- `S_NAME` (C,96) – 小地域名

`KEY_CODE` は `PREF`、`CITY`、`S_AREA` を連結して作られます。例:

```
KEY_CODE   PREF  CITY  S_AREA  PREF_NAME  CITY_NAME      S_NAME
11101002005 11    101   002005 埼玉県      さいたま市西区  三橋五丁目
```

### 数値コードの扱い

`pref_code`、`city_code`、`s_area_code` の各列はデータベース上では整数として保存されます。再びテキストとして出力する場合は、それぞれ 2 桁、3 桁、6 桁という元の桁数を維持できるよう先頭に 0 を補完してください。テキストデータを取り込む際には、桁数を確認したうえで先頭の 0 を除去して整数として保存する必要があります。

## 正規化テーブル

### prefectures
| column     | type    | details                          |
|----------- |-------- |--------------------------------- |
| prefecture_id | INTEGER PK AUTOINCREMENT | 自動採番の ID |
| pref_code  | INTEGER UNIQUE | 2 桁の都道府県コード (`PREF`) |
| pref_name  | TEXT    | 都道府県名 (`PREF_NAME`)       |

`pref_code` は元の都道府県コードで、重複を許さない一意制約を設けます。

### cities
| column    | type    | details                                             |
|---------- |-------  |---------------------------------------------------- |
| city_id   | INTEGER PK AUTOINCREMENT | 自動採番の市区町村 ID |
| pref_code | INTEGER FK | `prefectures.pref_code` への外部キー            |
| city_code | INTEGER    | 3 桁の市区町村コード (`CITY`)                     |
| city_name | TEXT    | 市区町村名 (`CITY_NAME`)                             |

`pref_code` と `city_code` の組み合わせが一意となるよう制約を設けます。

### sub_areas
| column      | type      | details                                       |
|------------ |--------- |---------------------------------------------- |
| sub_area_id | INTEGER PK AUTOINCREMENT | 自動採番の小地域 ID |
| s_area_code | INTEGER FK | 6 桁の小地域コード (`S_AREA`)                |
| city_id     | INTEGER FK | `cities.city_id` への外部キー                |
| prefecture_id | INTEGER FK | `prefectures.prefecture_id` への外部キー |
| s_name      | TEXT      | 小地域名 (`S_NAME`)                           |

このテーブルでは `s_area_code`、`city_id`、`prefecture_id` の組み合わせが一意に
なるよう制約を設けます。

`HCODE`、`AREA`、`PERIMETER` などの追加属性は、必要に応じて `s_area_code` をキーとした補助テーブルに格納できます。

このスキーマでは、都道府県および市区町村の情報をそれぞれ一度だけ保存し、`city_id` 外部キーを通じて小地域と関連付けることで冗長性を排除します。

