
import sqlite3
from pathlib import Path


def test_total_vendas():
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "data" / "salesflow.db"

    with sqlite3.connect(db_path) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM vendas"
        ).fetchone()[0]

    assert total == 10


def test_nao_existem_vendas_duplicadas():
    import pandas as pd
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    arquivo = base_dir / "data" / "processed" / "vendas.csv"

    df = pd.read_csv(arquivo)

    assert not df["id_venda"].duplicated().any()

def test_nao_existem_vendas_sem_cliente():
    import pandas as pd
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    arquivo = base_dir / "data" / "processed" / "vendas.csv"

    df = pd.read_csv(arquivo)

    assert df["id_cliente"].notna().all()

def test_quantidade_venda_corrigida():
    import pandas as pd
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    arquivo = base_dir / "data" / "processed" / "vendas.csv"

    df = pd.read_csv(arquivo)
    quantidade = df.loc[df["id_venda"] == 1008, "quantidade"].iloc[0]

    assert quantidade == 2