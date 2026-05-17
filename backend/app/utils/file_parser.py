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


def parse_file(source: str | io.BytesIO) -> pd.DataFrame:
    if isinstance(source, io.BytesIO):
        source.seek(0)
        content = source.read()
        source.seek(0)
        buf = io.BytesIO(content)
        try:
            df = pd.read_csv(buf, encoding="utf-8")
        except UnicodeDecodeError:
            buf.seek(0)
            df = pd.read_csv(buf, encoding="latin1")
        except Exception:
            buf.seek(0)
            df = pd.read_excel(buf, engine="openpyxl")
        df = _clean_dataframe(df)
        return df

    source_str = str(source)

    if source_str.startswith(("http://", "https://")):
        import httpx
        resp = httpx.get(source_str, timeout=30)
        resp.raise_for_status()
        buf = io.BytesIO(resp.content)
        try:
            df = pd.read_csv(buf, encoding="utf-8")
        except Exception:
            buf.seek(0)
            df = pd.read_excel(buf, engine="openpyxl")
        df = _clean_dataframe(df)
        return df

    ext = Path(source_str).suffix.lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(source_str, encoding="utf-8")
        elif ext == ".xlsx":
            df = pd.read_excel(source_str, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except UnicodeDecodeError:
        df = pd.read_csv(source_str, encoding="latin1")
    except Exception as e:
        raise ValueError(f"Failed to parse file: {e}")

    df = _clean_dataframe(df)
    return df


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
