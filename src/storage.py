import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "bcb.db"


def save_series(df: pd.DataFrame, tabela: str) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out.index.name = out.index.name or "data"
    with sqlite3.connect(DB_PATH) as conn:
        out.to_sql(tabela, conn, if_exists="replace", index=True)


def load_series(tabela: str) -> pd.DataFrame | None:
    if not DB_PATH.exists():
        return None
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (tabela,),
        )
        if cur.fetchone() is None:
            return None
        df = pd.read_sql(f"SELECT * FROM {tabela}", conn, parse_dates=["data"])
    return df.set_index("data")
