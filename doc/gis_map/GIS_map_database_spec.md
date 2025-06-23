# GIS Map データベース仕様

このドキュメントでは、国土数値情報「行政区域データ (GIS Map, 旧N03)」の DBF ファイルを取り込み、正規化した SQLite データベースへ格納するためのスキーマを説明します。

## 正規化テーブル

### prefectures
| column | type | details |
|--------|------|--------------------------------|
| prefecture_id | INTEGER PK AUTOINCREMENT | 自動採番の ID |
| pref_code | INTEGER UNIQUE | 2 桁の都道府県コード |
| pref_name | TEXT | 都道府県名 |

### subprefecters
| column | type | details |
|--------|------|--------------------------------|
| subpref_id | INTEGER PK AUTOINCREMENT | 自動採番の支庁 ID |
| subpref_name | TEXT UNIQUE | 支庁名または振興局名 |

### distincts
| column | type | details |
|--------|------|--------------------------------|
| distinct_id | INTEGER PK AUTOINCREMENT | 自動採番の広域行政区 ID |
| distinct_name | TEXT UNIQUE | 広域行政区名 |

### wards
| column | type | details |
|--------|------|--------------------------------|
| ward_id | INTEGER PK AUTOINCREMENT | 自動採番の政令市区 ID |
| ward_name | TEXT UNIQUE | 政令市区名 |

### cities
| column | type | details |
|--------|------|------------------------------------------------|
| city_id | INTEGER PK AUTOINCREMENT | 自動採番の市区町村 ID |
| pref_code | INTEGER FK | `prefectures.pref_code` への外部キー |
| city_code | INTEGER | 3 桁の市区町村コード |
| city_name | TEXT | 市区町村名 |
| subpref_id | INTEGER FK | `subprefecters.subpref_id` への外部キー (NULL 可) |
| distinct_id | INTEGER FK | `distincts.distinct_id` への外部キー (NULL 可) |
| ward_id | INTEGER FK | `wards.ward_id` への外部キー (NULL 可) |

`pref_code` と `city_code` の組み合わせに一意制約を設けます。

### areas_view
`cities` と各名称テーブルを結合した読み取り専用ビューです。市区町村に関連する名称をまとめて取得できます。

| column | type | details |
|--------|------|--------------------------------|
| city_id | INTEGER | `cities.city_id` |
| pref_code | INTEGER | `cities.pref_code` |
| city_code | INTEGER | `cities.city_code` |
| subpref_name | TEXT | `subprefecters.subpref_name` |
| distinct_name | TEXT | `distincts.distinct_name` |
| city_name | TEXT | `cities.city_name` |
| ward_name | TEXT | `wards.ward_name` |
