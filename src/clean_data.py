import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent  # raiz do projeto (pasta acima de src/)
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"

NUMEROS_POR_EXTENSO = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3,
    "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
}
PREPOSICOES = {"de", "da", "do", "das", "dos", "e"}


def converter_quantidade(serie):
    """Converte quantidades para número, aceitando também números por extenso."""
    texto = serie.astype(str).str.strip().str.lower()
    numerico = pd.to_numeric(texto, errors="coerce")
    return numerico.fillna(texto.map(NUMEROS_POR_EXTENSO))


def padronizar_nome(valor):
    if not isinstance(valor, str):
        return valor
    return re.sub(r"\s+", " ", valor).strip().title()


def padronizar_cidade(valor):
    if not isinstance(valor, str):
        return valor
    palavras = padronizar_nome(valor).split(" ")
    return " ".join(
        p.lower() if i > 0 and p.lower() in PREPOSICOES else p
        for i, p in enumerate(palavras)
    )


def _rejeitar(df, mascara, motivo, rejeitados):
    """Separa as linhas marcadas em `mascara`, registrando-as como rejeitadas."""
    if mascara.any():
        rejeitadas = df[mascara].copy()
        rejeitadas["motivo_rejeicao"] = motivo
        rejeitados.append(rejeitadas)
        logger.warning("%d venda(s) rejeitada(s): %s", len(rejeitadas), motivo)
    return df[~mascara]


def limpar_dados(raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR):
    raw_dir, processed_dir = Path(raw_dir), Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    df_venda = pd.read_csv(raw_dir / "vendas.csv")
    df_cliente = pd.read_csv(raw_dir / "clientes.csv")
    df_produto = pd.read_csv(raw_dir / "produtos.csv")

    total_inicial = len(df_venda)
    rejeitados = []

    # Duplicatas exatas são descartadas; mesmo id_venda com valores diferentes é erro
    df_venda = _rejeitar(
        df_venda, df_venda.duplicated(keep="first"), "venda duplicada", rejeitados
    )
    conflitos = df_venda.loc[df_venda["id_venda"].duplicated(keep=False), "id_venda"]
    if not conflitos.empty:
        raise ValueError(
            f"id_venda repetido com valores conflitantes: {sorted(conflitos.unique())}"
        )

    df_venda = _rejeitar(
        df_venda, df_venda["id_cliente"].isna(), "cliente não identificado", rejeitados
    )

    # Quantidade: número (inclusive por extenso), inteiro e maior que zero
    df_venda = df_venda.assign(_qtd=converter_quantidade(df_venda["quantidade"]))
    qtd_invalida = (
        df_venda["_qtd"].isna()
        | (df_venda["_qtd"] <= 0)
        | (df_venda["_qtd"] % 1 != 0)
    )
    df_venda = _rejeitar(df_venda, qtd_invalida, "quantidade inválida", rejeitados)

    # Preço unitário: numérico e maior que zero
    df_venda = df_venda.assign(_preco=pd.to_numeric(df_venda["preco_unitario"], errors="coerce"))
    df_venda = _rejeitar(
        df_venda,
        df_venda["_preco"].isna() | (df_venda["_preco"] <= 0),
        "preço unitário inválido",
        rejeitados,
    )

    # Data: formato AAAA-MM-DD
    df_venda = df_venda.assign(
        _data=pd.to_datetime(df_venda["data_venda"], format="%Y-%m-%d", errors="coerce")
    )
    df_venda = _rejeitar(df_venda, df_venda["_data"].isna(), "data inválida", rejeitados)

    df_venda = df_venda.assign(
        quantidade=df_venda["_qtd"].astype(int),
        preco_unitario=df_venda["_preco"],
        data_venda=df_venda["_data"].dt.strftime("%Y-%m-%d"),
        id_cliente=df_venda["id_cliente"].astype(int),
    ).drop(columns=["_qtd", "_preco", "_data"])

    colunas_auxiliares = ["_qtd", "_preco", "_data"]
    if rejeitados:
        df_rejeitados = pd.concat(rejeitados).drop(columns=colunas_auxiliares, errors="ignore")
    else:
        df_rejeitados = pd.DataFrame(columns=[*df_venda.columns, "motivo_rejeicao"])

    # Padronizar clientes
    df_cliente["nome"] = df_cliente["nome"].map(padronizar_nome)
    df_cliente["cidade"] = df_cliente["cidade"].map(padronizar_cidade)
    df_cliente["estado"] = df_cliente["estado"].str.strip().str.upper()

    df_venda.to_csv(processed_dir / "vendas.csv", index=False, encoding="utf-8")
    df_cliente.to_csv(processed_dir / "clientes.csv", index=False, encoding="utf-8")
    df_produto.to_csv(processed_dir / "produtos.csv", index=False, encoding="utf-8")
    df_rejeitados.to_csv(processed_dir / "vendas_rejeitadas.csv", index=False, encoding="utf-8")

    logger.info(
        "Limpeza concluída: %d vendas lidas, %d aprovadas, %d rejeitadas",
        total_inicial, len(df_venda), len(df_rejeitados),
    )
    return {"lidas": total_inicial, "aprovadas": len(df_venda), "rejeitadas": len(df_rejeitados)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    limpar_dados()
