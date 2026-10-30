import shutil
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from src.clean_data import (
    converter_quantidade,
    limpar_dados,
    padronizar_cidade,
    padronizar_nome,
)
from src.load_data import carregar_dados
from src.merge_data import integrar_dados

RAW_REAL = Path(__file__).resolve().parent.parent / "data" / "raw"

CLIENTES = "id_cliente,nome,cidade,estado\n1,  Ana   Souza ,rio de janeiro, rj\n"
PRODUTOS = "id_produto,nome_produto,categoria,preco_referencia\n101,Teclado,Perifericos,250.0\n"
CABECALHO_VENDAS = "id_venda,id_cliente,id_produto,quantidade,preco_unitario,data_venda\n"


def montar_raw(tmp_path, vendas):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "vendas.csv").write_text(CABECALHO_VENDAS + vendas, encoding="utf-8")
    (raw / "clientes.csv").write_text(CLIENTES, encoding="utf-8")
    (raw / "produtos.csv").write_text(PRODUTOS, encoding="utf-8")
    return raw


def rodar_limpeza(tmp_path, vendas):
    raw = montar_raw(tmp_path, vendas)
    processed = tmp_path / "processed"
    resumo = limpar_dados(raw, processed)
    return resumo, processed


# --- funções de padronização -------------------------------------------------

def test_padronizar_nome_colapsa_espacos():
    assert padronizar_nome("  carla   mendes ") == "Carla Mendes"


def test_padronizar_cidade_mantem_preposicoes_minusculas():
    assert padronizar_cidade("rio de janeiro") == "Rio de Janeiro"


def test_converter_quantidade_aceita_extenso():
    resultado = converter_quantidade(pd.Series(["2", "dois", "abc", " 3 "]))
    assert resultado.iloc[0] == 2
    assert resultado.iloc[1] == 2
    assert pd.isna(resultado.iloc[2])
    assert resultado.iloc[3] == 3


# --- regras de limpeza -------------------------------------------------------

def test_duplicata_exata_e_rejeitada(tmp_path):
    vendas = "1,1,101,1,250.0,2026-01-01\n1,1,101,1,250.0,2026-01-01\n"
    resumo, processed = rodar_limpeza(tmp_path, vendas)

    assert resumo == {"lidas": 2, "aprovadas": 1, "rejeitadas": 1}
    rejeitadas = pd.read_csv(processed / "vendas_rejeitadas.csv")
    assert rejeitadas["motivo_rejeicao"].tolist() == ["venda duplicada"]


def test_mesmo_id_com_valores_diferentes_levanta_erro(tmp_path):
    vendas = "1,1,101,1,250.0,2026-01-01\n1,1,101,2,250.0,2026-01-01\n"
    with pytest.raises(ValueError, match="conflitantes"):
        rodar_limpeza(tmp_path, vendas)


@pytest.mark.parametrize(
    "linha, motivo",
    [
        (",101,1,250.0,2026-01-01", "cliente não identificado"),
        ("1,101,0,250.0,2026-01-01", "quantidade inválida"),
        ("1,101,1.5,250.0,2026-01-01", "quantidade inválida"),
        ("1,101,muitas,250.0,2026-01-01", "quantidade inválida"),
        ("1,101,1,-5,2026-01-01", "preço unitário inválido"),
        ("1,101,1,,2026-01-01", "preço unitário inválido"),
        ("1,101,1,250.0,31/01/2026", "data inválida"),
    ],
)
def test_vendas_invalidas_sao_rejeitadas_com_motivo(tmp_path, linha, motivo):
    resumo, processed = rodar_limpeza(tmp_path, f"1,{linha}\n")

    assert resumo["aprovadas"] == 0
    rejeitadas = pd.read_csv(processed / "vendas_rejeitadas.csv")
    assert rejeitadas["motivo_rejeicao"].tolist() == [motivo]


def test_quantidade_por_extenso_e_convertida(tmp_path):
    _, processed = rodar_limpeza(tmp_path, "1,1,101,dois,250.0,2026-01-01\n")

    vendas = pd.read_csv(processed / "vendas.csv")
    assert vendas["quantidade"].tolist() == [2]
    assert pd.api.types.is_integer_dtype(vendas["quantidade"])


def test_clientes_sao_padronizados(tmp_path):
    _, processed = rodar_limpeza(tmp_path, "1,1,101,1,250.0,2026-01-01\n")

    cliente = pd.read_csv(processed / "clientes.csv").iloc[0]
    assert cliente["nome"] == "Ana Souza"
    assert cliente["cidade"] == "Rio de Janeiro"
    assert cliente["estado"] == "RJ"


# --- integração e carga ------------------------------------------------------

def test_integracao_rejeita_cliente_inexistente(tmp_path):
    _, processed = rodar_limpeza(tmp_path, "1,1,101,1,250.0,2026-01-01\n")
    pd.DataFrame(
        {"id_venda": [2], "id_cliente": [99], "id_produto": [101], "quantidade": [1],
         "preco_unitario": [250.0], "data_venda": ["2026-01-02"]}
    ).to_csv(processed / "vendas.csv", index=False)

    with pytest.raises(ValueError, match="clientes inexistentes"):
        integrar_dados(processed)


# --- pipeline completo sobre os dados reais (copiados para tmp_path) ----------

@pytest.fixture(scope="module")
def pipeline_real(tmp_path_factory):
    base = tmp_path_factory.mktemp("pipeline")
    raw = base / "raw"
    shutil.copytree(RAW_REAL, raw)
    processed = base / "processed"
    db = base / "salesflow.db"

    resumo = limpar_dados(raw, processed)
    integrar_dados(processed)
    carregar_dados(processed, db)
    return resumo, processed, db


def test_pipeline_resumo(pipeline_real):
    resumo, _, _ = pipeline_real
    # 12 lidas: 1 duplicata (1007) e 1 sem cliente (1009) rejeitadas; 1008 ("dois") é corrigida
    assert resumo == {"lidas": 12, "aprovadas": 10, "rejeitadas": 2}


def test_pipeline_faturamento_total(pipeline_real):
    _, _, db = pipeline_real
    with sqlite3.connect(db) as conn:
        total = conn.execute("SELECT ROUND(SUM(quantidade * preco_unitario), 2) FROM vendas").fetchone()[0]
    assert total == 18884.70


def test_pipeline_venda_1008_corrigida(pipeline_real):
    _, _, db = pipeline_real
    with sqlite3.connect(db) as conn:
        quantidade = conn.execute("SELECT quantidade FROM vendas WHERE id_venda = 1008").fetchone()[0]
    assert quantidade == 2


def test_pipeline_integracao_preserva_total_de_vendas(pipeline_real):
    _, processed, _ = pipeline_real
    vendas = pd.read_csv(processed / "vendas.csv")
    integradas = pd.read_csv(processed / "vendas_integradas.csv")
    assert len(integradas) == len(vendas)


def test_banco_tem_chave_primaria_em_id_venda(pipeline_real):
    _, _, db = pipeline_real
    with sqlite3.connect(db) as conn:
        pk = [c[1] for c in conn.execute("PRAGMA table_info(vendas)") if c[5]]
    assert pk == ["id_venda"]
