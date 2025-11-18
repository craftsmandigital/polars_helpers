""""
# --- SOLUTION ---

# 1. Define the list of all columns you want to convert to dates
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

# Filter the list to only include columns that actually exist in the DataFrame
# This prevents errors if your CSV file is missing a column.
date_cols_in_df = [col for col in date_cols_to_convert if col in df.columns]


# 2. Chain the operations using .pipe()
processed_df = (
    df
    .pipe(parse_fødselsnummer)
    .pipe(add_full_name)
    .pipe(convert_string_dates, date_columns=date_cols_in_df)
)
"""

import polars as pl
from typing import List

def build_concat_expr(
    input_columns: List[str], 
    output_column: str, 
    separator: str = " "
) -> pl.Expr:
    """
    Builds a robust Polars expression to concatenate multiple string columns.

    This function creates the logic but does not execute it. The returned
    expression can be used in .select(), .with_columns(), etc.

    Args:
        input_columns: A list of column names to concatenate.
        output_column: The desired name for the new column.
        separator: The string to place between each value.

    Returns:
        A Polars expression.

    Example:
        df.select(
            build_concat_expr(
                input_columns=["FirstName", "MidleName"],
                output_column="Full name",
                separator=" "
            ), ... other collumns ...
    """
    # 1. Create a list of expressions, applying the robust checks to each column
    expressions_to_concat = [
        pl.col(c).cast(pl.String).fill_null("") for c in input_columns
    ]
    
    # 2. Build the final expression by concatenating, stripping, and aliasing
    return (
        pl.concat_str(expressions_to_concat, separator="ZQ") # Dummy separator
        .str.strip_chars()
        .str.replace_all(r"(ZQ){2,}", separator) # remove all sepparators in row, keep one and replace with desired separator
        .alias(output_column)
    )



def add_full_name(df: pl.DataFrame) -> pl.DataFrame:
    """
    Pipe-able function to robustly concatenate 'Fornavn' and 'Mellomnavn'
    into a new column named 'Navn'.
    """
    print("-> Adding 'Navn' column...")
    # Call the generic function to create the expression we need
    name_expression = build_concat_expr(
        input_columns=["Fornavn", "Mellomnavn"], 
        output_column="Navn",
        separator=" "
    )
    
    # Use that expression to add the column
    return df.with_columns(name_expression)



def convert_string_dates(
    df: pl.DataFrame, 
    date_columns: List[str], 
    date_format: str = "%d.%m.%Y"  # <-- The new optional parameter with its default value
) -> pl.DataFrame:
    """
    Pipe-able function to convert a list of string columns to Polars Date type.

    It uses a default date format of "DD.MM.YYYY" but allows a custom format
    to be passed in.

    Args:
        df: The input DataFrame (from .pipe()).
        date_columns: A list of column names to convert.
        date_format: The format string for parsing dates (e.g., "%Y-%m-%d").
                     Defaults to "%d.%m.%Y".
    """
    # Filter the list to only act on columns that actually exist in the DataFrame
    # This makes the function safer and prevents errors.
    cols_in_df = [col for col in date_columns if col in df.columns]

    if not cols_in_df:
        return df # Return the DataFrame unchanged if no columns match

    print(f"-> Converting date columns ({cols_in_df}) using format: '{date_format}'")
    
    return df.with_columns(
        # The `date_format` variable is now used directly here
        pl.col(cols_in_df).str.to_date(format=date_format, strict=False)
    )







def parse_fødselsnummer(df: pl.DataFrame) -> pl.DataFrame:
    """
    Pipe-able function to parse a Norwegian 'Fødselsnummer' column
    and create 'Fødselsdato' (Date) and 'Kjønn' (String) columns.
    
    Assumes the 'Fødselsnummer' is an 11-digit string.
    """
    print("-> Parsing 'Fødselsnummer' to generate 'Fødselsdato' and 'Kjønn'...")

    # Use a common expression for the source column to keep it clean
    fnr_col = pl.col("Fødselsnummer")


    # --- 1. Logic for Fødselsdato ---
    
    # Determine the century ('19' or '20') based on the 7th digit (index 6)
    century_expr = (
        pl.when(fnr_col.str.slice(6, 1) > "4")
        .then(pl.lit("20"))
        .otherwise(pl.lit("19"))
    )
    
    # Extract the other date parts
    year_part_expr = fnr_col.str.slice(4, 2)
    month_part_expr = fnr_col.str.slice(2, 2)
    day_part_expr = fnr_col.str.slice(0, 2)
    
    # Combine the parts into a full YYYY-MM-DD string and convert to a date
    birth_date_expr = (
        pl.format(
            "{}{}-{}-{}", century_expr, year_part_expr, month_part_expr, day_part_expr
        )
        .str.to_date(format="%Y-%m-%d", strict=False)

        .alias("Fødselsdato")
    )

    # --- 2. Logic for Kjønn ---
    
    # The 9th digit (index 8) determines gender. Even = Female.
    gender_expr = (
        pl.when(fnr_col.str.slice(8, 1).cast(pl.Int8).mod(2) == 0)
        .then(pl.lit("Kvinne"))
        .otherwise(pl.lit("Mann"))
        .alias("Kjønn")
    )
    
    # --- 3. Return the DataFrame with the new columns ---
    return df.with_columns(
        birth_date_expr,
        gender_expr
    )
