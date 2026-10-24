import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def integrar_dados():
    df_venda = pd.read_csv(PROCESSED_DIR / "vendas.csv")
    df_cliente = pd.read_csv(PROCESSED_DIR / "clientes.csv")
    df_produto = pd.read_csv(PROCESSED_DIR / "produtos.csv")

    df_final = df_venda.merge(df_cliente, on="id_cliente", how="left")
    df_final = df_final.merge(df_produto, on="id_produto", how="left")

    df_final.to_csv(
        PROCESSED_DIR / "vendas_integradas.csv",
        index=False,
        encoding="utf-8"
    )

    print(f"Integração concluída! Total de registros: {len(df_final)}")


if __name__ == "__main__":
    integrar_dados()