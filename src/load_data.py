import logging
import sqlite3
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "data" / "salesflow.db"

SCHEMA = """
DROP TABLE IF EXISTS vendas;
CREATE TABLE vendas (
    id_venda         INTEGER PRIMARY KEY,
    id_cliente       INTEGER NOT NULL,
    id_produto       INTEGER NOT NULL,
    quantidade       INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario   REAL    NOT NULL CHECK (preco_unitario > 0),
    data_venda       TEXT    NOT NULL,  -- AAAA-MM-DD
    nome             TEXT    NOT NULL,
    cidade           TEXT    NOT NULL,
    estado           TEXT    NOT NULL,
    nome_produto     TEXT    NOT NULL,
    categoria        TEXT    NOT NULL,
    preco_referencia REAL    NOT NULL
);
CREATE INDEX idx_vendas_cidade  ON vendas (cidade);
CREATE INDEX idx_vendas_produto ON vendas (id_produto);
CREATE INDEX idx_vendas_data    ON vendas (data_venda);
"""


def carregar_dados(processed_dir=PROCESSED_DIR, db_path=DB_PATH):
    df = pd.read_csv(Path(processed_dir) / "vendas_integradas.csv")

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        df.to_sql("vendas", conn, if_exists="append", index=False)
        total = conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0]

    logger.info("Carga concluída: %d registros no banco", total)
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    carregar_dados()
