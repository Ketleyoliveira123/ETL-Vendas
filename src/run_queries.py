import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "salesflow.db"
QUERIES_PATH = Path(__file__).resolve().parent / "queries.sql"


def carregar_consultas(caminho=QUERIES_PATH):
    """Lê queries.sql: cada consulta é precedida por um comentário '-- Título'."""
    consultas = {}
    titulo = None
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        if linha.startswith("--"):
            titulo = linha[2:].strip()
            consultas[titulo] = ""
        elif titulo:
            consultas[titulo] += linha + "\n"
    return consultas


def executar_consultas(db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
        for titulo, sql in carregar_consultas().items():
            print(f"\n--- {titulo} ---")
            for linha in conn.execute(sql).fetchall():
                print(linha)


if __name__ == "__main__":
    executar_consultas()
