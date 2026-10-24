import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def limpar_dados():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Carregar os dados originais
    df_venda = pd.read_csv(RAW_DIR / "vendas.csv")
    df_cliente = pd.read_csv(RAW_DIR / "clientes.csv")
    df_produto = pd.read_csv(RAW_DIR / "produtos.csv")

    # Remover vendas duplicadas
    df_venda = df_venda.drop_duplicates()

    # Remover vendas sem cliente identificado
    df_venda = df_venda.dropna(subset=["id_cliente"])

    # Converter quantidade para número
    df_venda["quantidade"] = pd.to_numeric(
        df_venda["quantidade"], errors="coerce"
    )

    # Corrigir a quantidade da venda 1008
    df_venda.loc[df_venda["id_venda"] == 1008, "quantidade"] = 2

    # Limpar nomes e padronizar cidades
    df_cliente["nome"] = df_cliente["nome"].str.strip().str.title()
    df_cliente["cidade"] = df_cliente["cidade"].str.strip().str.title()

    # Salvar dados tratados
    df_venda.to_csv(PROCESSED_DIR / "vendas.csv", index=False, encoding="utf-8")
    df_cliente.to_csv(PROCESSED_DIR / "clientes.csv", index=False, encoding="utf-8")
    df_produto.to_csv(PROCESSED_DIR / "produtos.csv", index=False, encoding="utf-8")

    print("Limpeza concluída!")


if __name__ == "__main__":
    limpar_dados()