# Polars helper functions

## Installation

```bash
pip install git+https://github.com/craftsmandigital/polars_helpers.git
```

### Using uv

```bash
 uv add git+https://github.com/craftsmandigital/polars_helpers.git
```

## Usage

``` python
from polars_helpers import general
```

``` python
# 1. Define the list of all columns you want to convert to dates
# Later used in function "convert_string_dates"
date_cols_to_convert = [
    "Fødselsdato",
    "Dødsdato",
    "Opprettet",
    "Startdato 2",
    "Sluttdato 2",
    "Startdato 3",
    "Sluttdato 3",
    "Innmeldt dato 1",
    "Utmeldt dato 1",
    "Begravelse Dato",
    "Dåp Dato",
    "Ektevielse Dato",
    "KID Dato",
    "Minnetale URL Dato"
]

# 2. Chain the operations using .pipe()
processed_df = (
    df
    .pipe(general.parse_fødselsnummer)
    .pipe(general.add_full_name)
    .pipe(general.convert_string_dates, date_columns=date_cols_in_df)
)

```

## Functions
### add_full_name()
``` python
def add_full_name(df: pl.DataFrame) -> pl.DataFrame:
```
Pipe-able function to robustly concatenate 'Fornavn' and 'Mellomnavn' into a new column named 'Navn'.

---


### parse_fødselsnummer()
``` python
def parse_fødselsnummer(df: pl.DataFrame) -> pl.DataFrame:
```
Pipe-able function to parse a Norwegian 'Fødselsnummer' column and create 'Fødselsdato' (Date) and 'Kjønn' (String) columns.<br>
Assumes the 'Fødselsnummer' is an 11-digit string.

--- 

### convert_string_dates()
``` python
def convert_string_dates(
    df: pl.DataFrame,              # The input DataFrame (from .pipe()).
    date_columns: List[str],       # A list of column names to convert.
    date_format: str = "%d.%m.%Y"  # Optional parameter for parsing dates.
) -> pl.DataFrame:
```
Pipe-able function to convert a list of string columns to Polars Date type.<br>
It uses a default date format of "DD.MM.YYYY" but allows a custom format to be passed in.
