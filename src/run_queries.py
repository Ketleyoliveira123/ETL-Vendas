
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "salesflow.db"

consultas = {
    "Total de vendas": """
        SELECT COUNT(*) FROM vendas;
    """,
    "Faturamento total": """
        SELECT ROUND(SUM(quantidade * preco_unitario), 2)
        FROM vendas;
    """,
    "Faturamento por cidade": """
        SELECT cidade,
               ROUND(SUM(quantidade * preco_unitario), 2)
        FROM vendas
        GROUP BY cidade
        ORDER BY 2 DESC;
    """,
    "Produtos mais vendidos": """
        SELECT nome_produto, CAST(SUM(quantidade) AS INTEGER)
        FROM vendas
        GROUP BY nome_produto
        ORDER BY 2 DESC;
    """
}

with sqlite3.connect(DB_PATH) as conn:
    for titulo, sql in consultas.items():
        print(f"\n--- {titulo} ---")
        resultado = conn.execute(sql)
        for linha in resultado.fetchall():
            print(linha)
