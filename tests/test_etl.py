
import sqlite3
from pathlib import Path

import pandas as pd

from src.clean_data import limpar_dados
from src.merge_data import integrar_dados
from src.load_data import carregar_dados

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "salesflow.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def setup_module():
    """Executa o pipeline antes dos testes."""
    limpar_dados()
    integrar_dados()
    carregar_dados()


def test_total_vendas():
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0]

    assert total == 9


def test_nao_existem_vendas_duplicadas():
    df = pd.read_csv(PROCESSED_DIR / "vendas.csv")
    assert not df["id_venda"].duplicated().any()


def test_nao_existem_vendas_sem_cliente():
    df = pd.read_csv(PROCESSED_DIR / "vendas.csv")
    assert df["id_cliente"].notna().all()


def test_quantidades_sao_validas():
    df = pd.read_csv(PROCESSED_DIR / "vendas.csv")

    assert df["quantidade"].notna().all()
    assert (df["quantidade"] > 0).all()
    assert pd.api.types.is_numeric_dtype(df["quantidade"])


def test_integracao_preserva_total_de_vendas():
    vendas = pd.read_csv(PROCESSED_DIR / "vendas.csv")
    integradas = pd.read_csv(PROCESSED_DIR / "vendas_integradas.csv")

    assert len(integradas) == len(vendas)
