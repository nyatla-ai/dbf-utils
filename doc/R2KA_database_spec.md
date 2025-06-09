# R2KA データベース仕様

このドキュメントでは、`dev/r2ka11.dbf` に含まれる R2KA シェープファイルの属性データを正規化して格納するためのスキーマを説明します。

このデータセットは埼玉県内の行政区域ポリゴンを含みます。主な項目は以下のとおりです。

- `KEY_CODE` (C,11) – 下記コードを連結した一意の識別子（ソースデータのみに存在）
- `PREF` (C,2) – 都道府県コード
- `CITY` (C,3) – 市区町村コード
- `S_AREA` (C,6) – 市区町村内の小地域コード
- `PREF_NAME` (C,12) – 都道府県名
- `CITY_NAME` (C,16) – 市区町村名
- `S_NAME` (C,96) – 小地域名

`S_AREA` は上位 4 桁が字コード、下位 2 桁が丁目番号で構成されます。例として `002005` は字コード `0020`、丁目番号 `05` を表します。`S_NAME` はこれらを連結した文字列であり、同じ字コードを持つレコードの `S_NAME` から共通部分を取り除いた残りが丁目名となります。

`KEY_CODE` は `PREF`、`CITY`、`S_AREA` を連結して作られます。例:

```
KEY_CODE   PREF  CITY  S_AREA  PREF_NAME  CITY_NAME      S_NAME
11101002005 11    101   002005 埼玉県      さいたま市西区  三橋五丁目
```

### 数値コードの扱い

`pref_code`、`city_code`、`s_area_code` の各列はデータベース上では整数として保存されます。再びテキストとして出力する場合は、それぞれ 2 桁、3 桁、6 桁という元の桁数を維持できるよう先頭に 0 を補完してください。CSV を読み込む際には桁数を確認したうえで先頭の 0 を除去して整数として保存する必要があります。

CSV から取り込む際、`PREF`、`CITY`、`S_AREA` の各値はそれぞれ 2 桁、3 桁、6 桁の数字であるかを検証します。桁数が合わない、または数値でない行は読み飛ばされます。

### 字名と丁目名の抽出

同じ字コードを持つレコードの `S_NAME` から先頭の共通部分を求め、それを字名とみなします。残りの部分が丁目名になります。たとえば

```
本町一丁目
本町二丁目
本町三丁目
```

という 3 行からは字名「本町」と丁目名「一丁目」「二丁目」「三丁目」を取得します。

## 正規化テーブル

### prefectures
| column        | type                        | details                              |
|---------------|-----------------------------|--------------------------------------|
| prefecture_id | INTEGER PK AUTOINCREMENT   | 自動採番の ID                        |
| pref_code     | INTEGER UNIQUE             | 2 桁の都道府県コード (`PREF`)        |
| pref_name     | TEXT                       | 都道府県名 (`PREF_NAME`)             |

### cities
| column   | type                      | details |
|----------|---------------------------|--------------------------------|
| city_id  | INTEGER PK AUTOINCREMENT | 自動採番の市区町村 ID |
| pref_code| INTEGER FK               | `prefectures.pref_code` への外部キー |
| city_code| INTEGER                  | 3 桁の市区町村コード (`CITY`) |
| city_name| TEXT                     | 市区町村名 (`CITY_NAME`) |

`pref_code` と `city_code` の組み合わせに一意制約を設けます.

### areas
| column     | type                      | details |
|------------|---------------------------|------------------------------|
| area_id    | INTEGER PK AUTOINCREMENT | 自動採番の字 ID |
| area_name  | TEXT                     | 字名 |

### sections
| column        | type                      | details                                                    |
|---------------|---------------------------|------------------------------------------------------------|
| section_id    | INTEGER PK AUTOINCREMENT | 自動採番の丁目 ID |
| section_name  | TEXT                     | 丁目名 |

### sub_areas
| column        | type                      | details |
|---------------|---------------------------|---------------------------------------|
| sub_area_id   | INTEGER PK AUTOINCREMENT | 自動採番の小地域 ID |
| s_area_code   | INTEGER                  | 6 桁の小地域コード (`S_AREA`) |
| area_id       | INTEGER FK               | `areas.area_id` への外部キー |
| section_id    | INTEGER FK               | `sections.section_id` への外部キー |
| city_id       | INTEGER FK               | `cities.city_id` への外部キー |
| prefecture_id | INTEGER FK               | `prefectures.prefecture_id` への外部キー |

`sub_areas` では `s_area_code`、`city_id`、`prefecture_id` の組み合わせが一意となるよう制約を設けます。追加属性は `s_area_code` をキーとした補助テーブルに格納してください。

