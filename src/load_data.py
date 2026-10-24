import pandas as pd
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "data" / "salesflow.db"


def carregar_dados():
    df = pd.read_csv(PROCESSED_DIR / "vendas_integradas.csv")

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("vendas", conn, if_exists="replace", index=False)

        total = pd.read_sql(
            "SELECT COUNT(*) AS total FROM vendas", conn
        ).iloc[0]["total"]

    print(f"Carga concluída! Registros no banco: {total}")


if __name__ == "__main__":
    carregar_dados()