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

1. `S_AREA` は 4 桁の字コードと 2 桁の丁目番号から構成され、`int(S_AREA/100)` と `S_AREA % 100` でそれぞれ取得できます。
2. 丁目番号が `0` の場合は丁目を持たないものとして扱い、`section_id` は `NULL` とします。このとき `S_NAME` 全体を `areas` のみへ登録します。
3. 上記以外の場合は、同じ字コードを持つレコードを CSV 内から抽出し、
   それらの `S_NAME` の先頭から共通する部分を `area_name` とします。
   各 `S_NAME` からその共通部分を取り除いた残りを `section_name` として登録します。

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
| section_id    | INTEGER FK               | `sections.section_id` への外部キー (NULL 可) |
| city_id       | INTEGER FK               | `cities.city_id` への外部キー |
| prefecture_id | INTEGER FK               | `prefectures.prefecture_id` への外部キー |

`sub_areas` では `s_area_code`、`city_id`、`prefecture_id` の組み合わせが一意となるよう制約を設けます。追加属性は `s_area_code` をキーとした補助テーブルに格納してください。

### codes_view
`sub_areas` と `cities`、`prefectures` を結合した読み取り専用ビューです。各コードを連結した `jis_code` 列を含みます。

| column | type | details |
|--------|------|--------------------------------------------------------------------------------|
| sub_area_id | INTEGER | `sub_areas.sub_area_id` |
| prefecture_code | INTEGER | `prefectures.pref_code` |
| city_code | INTEGER | `cities.city_code` |
| s_area_code | INTEGER | `sub_areas.s_area_code` |
| jis_code | INTEGER | `((prefecture_code*1000)+city_code)*1000000+s_area_code` |

## 地名 ID テーブル

R2KA の `sub_areas` は `PREF/CITY/S_AREA` に対応する統計区域コード単位のテーブルです。
一方、地図表示や辞書化では、同一の表示地名を同一 ID として扱う必要があります。
このため、表示地名単位の ID として `x_district_id` を定義します。

### 前提

`S_AREA` は表示地名そのものの ID ではなく、統計区域コードです。
そのため、異なる `S_AREA` が同じ表示地名を持つ場合があります。

例:

```
PREF/CITY/S_AREA  S_NAME
35/216/001301     大字小野田
35/216/001302     大字小野田
35/216/001303     大字小野田
```

この場合、`sub_areas` としては別の統計区域ですが、表示地名としては同じ地名へ名寄せします。

### x_districts

`x_districts` は、表示地名単位の ID を保持するテーブルです。
`x_district_id` は `0` から始まる連続整数とします。

| column | type | details |
|--------|------|---------|
| x_district_id | INTEGER PK | 表示地名 ID。0 から始まる連続整数 |
| prefecture_id | INTEGER FK | `prefectures.prefecture_id` |
| city_id | INTEGER FK | `cities.city_id` |
| area_id | INTEGER FK | `areas.area_id` |
| section_id | INTEGER | `sections.section_id`。丁目なしは `0` |
| first_sub_area_id | INTEGER FK | この地名が初めて出現した `sub_areas.sub_area_id` |

`section_id` は `NULL` ではなく `0` に正規化します。
これは SQLite の `UNIQUE` 制約で `NULL` が同一値として扱われないことを避けるためです。

次の組み合わせは一意でなければなりません。

```
UNIQUE(prefecture_id, city_id, area_id, section_id)
```

### x_sub_area_districts

`x_sub_area_districts` は、統計区域 ID から表示地名 ID への対応を保持するテーブルです。

| column | type | details |
|--------|------|---------|
| sub_area_id | INTEGER PK | `sub_areas.sub_area_id` |
| x_district_id | INTEGER FK | `x_districts.x_district_id` |

対応は多対一です。
複数の `sub_area_id` が同じ `x_district_id` に対応してよいものとします。

```
sub_area_id -> x_district_id
```

### x_district_id の採番規則

`x_district_id` は `sub_area_id` の出現順で採番します。

手順:

1. `sub_areas` を `sub_area_id` 昇順で走査する。
2. 各行から地名キーを作る。
3. 未登録の地名キーが出現したら、次の `x_district_id` を割り当てる。
4. すべての `sub_area_id` について `x_sub_area_districts` に対応を記録する。

地名キーは次の4要素です。

```
(prefecture_id, city_id, area_id, section_id_or_0)
```

疑似コード:

```python
next_id = 0
district_key_to_id = {}

for sub_area in sub_areas ORDER BY sub_area_id:
    key = (
        sub_area.prefecture_id,
        sub_area.city_id,
        sub_area.area_id,
        sub_area.section_id or 0,
    )

    if key not in district_key_to_id:
        district_key_to_id[key] = next_id
        insert into x_districts values (
            next_id,
            key.prefecture_id,
            key.city_id,
            key.area_id,
            key.section_id,
            sub_area.sub_area_id,
        )
        next_id += 1

    insert into x_sub_area_districts values (
        sub_area.sub_area_id,
        district_key_to_id[key],
    )
```

この規則により、`x_district_id` 昇順は地名の初出順になります。

### 階層順序制約

`x_district_id` 昇順に `x_districts` を走査したとき、地名階層は完全な入れ子順でなければなりません。

階層は次の4段です。

```
prefecture -> city -> area -> section
```

同じ上位 prefix が、別の prefix を挟んだ後で再出現してはなりません。

許容例:

```
A / X / a / 1
A / X / a / 2
A / X / b / 1
A / Y / c / 1
B / Z / d / 1
```

不正例:

```
A / X / a / 1
A / Y / b / 1
A / X / c / 1  # A/X が再出現
```

この制約に違反する場合、`x_districts` を階層データとしてシリアル化する処理は失敗しなければなりません。
不正な順序を自動で並べ替えてはなりません。

### 用途

ラスタ値が `codes_view.jis_code`、つまり `PREF/CITY/S_AREA` 由来の区域 ID である場合、次の2段階で表示地名 ID へ remap できます。

```
codes_view.jis_code -> sub_area_id -> x_district_id
```

`x_district_id` は、表示地名辞書や `GisWordBook` の index として使用できます。

```
x_district_id -> [prefecture, city, area, section]
```
