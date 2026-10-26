
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def integrar_dados():
    df_venda = pd.read_csv(PROCESSED_DIR / "vendas.csv")
    df_cliente = pd.read_csv(PROCESSED_DIR / "clientes.csv")
    df_produto = pd.read_csv(PROCESSED_DIR / "produtos.csv")

    # Validar IDs duplicados nas tabelas de referência
    if df_cliente["id_cliente"].duplicated().any():
        raise ValueError("Existem IDs de clientes duplicados.")

    if df_produto["id_produto"].duplicated().any():
        raise ValueError("Existem IDs de produtos duplicados.")

    # Identificar clientes e produtos inexistentes
    clientes_invalidos = ~df_venda["id_cliente"].isin(df_cliente["id_cliente"])
    produtos_invalidos = ~df_venda["id_produto"].isin(df_produto["id_produto"])
    
    if clientes_invalidos.any():
        raise ValueError("Existem vendas com clientes inexistentes.")

    if produtos_invalidos.any():
        raise ValueError("Existem vendas com produtos inexistentes.")

    # Validar os relacionamentos durante as junções
    df_final = df_venda.merge(
        df_cliente,
        on="id_cliente",
        how="left",
        validate="many_to_one"
    )

    df_final = df_final.merge(
        df_produto,
        on="id_produto",
        how="left",
        validate="many_to_one"
    )

    df_final.to_csv(
        PROCESSED_DIR / "vendas_integradas.csv",
        index=False,
        encoding="utf-8"
    )

    print(f"Integração concluída! Total de registros: {len(df_final)}")


if __name__ == "__main__":
    integrar_dados()
