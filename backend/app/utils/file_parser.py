import csv
import io
from pathlib import Path

import pandas as pd


ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


def validate_file(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def _decode_bytes(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin1", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(
        "Unable to read file encoding. Please save your CSV as UTF-8 and try again."
    )


def _guess_separator(sample: str) -> str | None:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return None


def _read_csv_text(text: str) -> pd.DataFrame:
    sample = "\n".join(text.splitlines()[:20])
    sniffed = _guess_separator(sample)

    strategies: list[dict] = []
    if sniffed:
        strategies.append({"sep": sniffed, "engine": "python"})
    strategies.extend(
        [
            {"sep": ",", "engine": "python"},
            {"sep": ";", "engine": "python"},
            {"sep": "\t", "engine": "python"},
            {"sep": None, "engine": "python"},
        ]
    )

    seen: set[str] = set()
    errors: list[str] = []
    for opts in strategies:
        sep = opts.get("sep")
        key = repr(sep)
        if key in seen:
            continue
        seen.add(key)

        try:
            df = pd.read_csv(io.StringIO(text), **opts)
            if len(df.columns) >= 1:
                return df
        except Exception as e:
            errors.append(str(e))

    first_error = errors[0] if errors else "unknown parse error"
    raise ValueError(
        "Could not parse CSV. Some rows have a different number of columns than the "
        "header — often caused by commas inside text fields that are not wrapped in "
        'quotes (e.g. "Product A, variant B"), or by using semicolon-separated data. '
        f"Open the file in Excel or Google Sheets, fix row formatting, and re-export. "
        f"Details: {first_error}"
    )


def _read_csv_bytes(buf: io.BytesIO) -> pd.DataFrame:
    buf.seek(0)
    text = _decode_bytes(buf.read())
    return _read_csv_text(text)


def _read_excel_bytes(buf: io.BytesIO) -> pd.DataFrame:
    buf.seek(0)
    return pd.read_excel(buf, engine="openpyxl")


def parse_file(source: str | io.BytesIO, file_ext: str | None = None) -> pd.DataFrame:
    if isinstance(source, io.BytesIO):
        ext = (file_ext or "").lower()
        if not ext:
            source.seek(0)
            header = source.read(4)
            source.seek(0)
            ext = ".xlsx" if header[:2] == b"PK" else ".csv"

        if ext == ".csv":
            df = _read_csv_bytes(source)
        elif ext == ".xlsx":
            df = _read_excel_bytes(source)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        return _clean_dataframe(df)

    source_str = str(source)
    ext = file_ext or Path(source_str).suffix.lower()

    if source_str.startswith(("http://", "https://")):
        import httpx

        resp = httpx.get(source_str, timeout=30)
        resp.raise_for_status()
        buf = io.BytesIO(resp.content)
        return parse_file(buf, file_ext=ext or ".csv")

    try:
        if ext == ".csv":
            with open(source_str, encoding="utf-8-sig") as f:
                df = _read_csv_text(f.read())
        elif ext == ".xlsx":
            df = pd.read_excel(source_str, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse file: {e}") from e

    return _clean_dataframe(df)


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip().replace("nan", None)

    return df.reset_index(drop=True)


def get_summary_stats(df: pd.DataFrame) -> dict:
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {str(col): int(df[col].isna().sum()) for col in df.columns},
        "missing_pct": {
            str(col): round(float(df[col].isna().mean() * 100), 2)
            for col in df.columns
        },
        "numeric_columns": [
            str(col) for col in df.columns if pd.api.types.is_numeric_dtype(df[col])
        ],
        "categorical_columns": [
            str(col)
            for col in df.columns
            if df[col].dtype == "object" and df[col].nunique() < len(df) * 0.5
        ],
        "date_columns": [
            str(col)
            for col in df.columns
            if "datetime" in str(df[col].dtype)
        ],
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
    }
