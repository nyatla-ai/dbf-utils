# R2KA Database Specification

This document describes a normalized schema for the R2KA shapefile attribute data
stored in `dev/r2ka11.dbf`.

The dataset contains administrative area polygons from Saitama Prefecture.  Fields
of interest are:

- `KEY_CODE` (C,11) – unique area identifier
- `PREF` (C,2) – prefecture code
- `CITY` (C,3) – city/ward/town code within the prefecture
- `S_AREA` (C,6) – sub‑area code within the city
- `PREF_NAME` (C,12) – prefecture name
- `CITY_NAME` (C,16) – city/ward/town name
- `S_NAME` (C,96) – sub‑area name

`KEY_CODE` is formed by concatenating `PREF`, `CITY` and `S_AREA`.  For example,

```
KEY_CODE   PREF  CITY  S_AREA  PREF_NAME  CITY_NAME      S_NAME
11101002005 11    101   002005 埼玉県      さいたま市西区  三橋五丁目
```

## Normalized Tables

### prefectures
| column     | type    | details                    |
|----------- |-------- |--------------------------- |
| pref_code  | TEXT PK | two‑digit code (`PREF`)    |
| pref_name  | TEXT    | name (`PREF_NAME`)         |

### cities
| column    | type    | details                                 |
|---------- |-------  |---------------------------------------- |
| city_id   | TEXT PK | concatenation of `pref_code` and `city_code` |
| pref_code | TEXT FK | references `prefectures.pref_code`      |
| city_code | TEXT    | three‑digit code (`CITY`)               |
| city_name | TEXT    | name (`CITY_NAME`)                      |

### sub_areas
| column     | type    | details                                   |
|----------- |-------  |------------------------------------------ |
| key_code   | TEXT PK | full identifier (`KEY_CODE`)              |
| city_id    | TEXT FK | references `cities.city_id`               |
| s_area     | TEXT    | six‑digit code (`S_AREA`)                 |
| s_name     | TEXT    | name (`S_NAME`)                           |

Additional attributes such as `HCODE`, `AREA`, `PERIMETER`, etc. may be stored in
an auxiliary table linked by `key_code` if required.

This schema removes redundancy by storing each prefecture and city only once,
while linking sub‑areas to their respective city via foreign keys.
