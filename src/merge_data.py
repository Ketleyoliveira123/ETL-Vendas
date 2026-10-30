import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def integrar_dados(processed_dir=PROCESSED_DIR):
    processed_dir = Path(processed_dir)

    df_venda = pd.read_csv(processed_dir / "vendas.csv")
    df_cliente = pd.read_csv(processed_dir / "clientes.csv")
    df_produto = pd.read_csv(processed_dir / "produtos.csv")

    # Validar IDs duplicados nas tabelas de referência e nas vendas
    if df_venda["id_venda"].duplicated().any():
        raise ValueError("Existem IDs de vendas duplicados.")

    if df_cliente["id_cliente"].duplicated().any():
        raise ValueError("Existem IDs de clientes duplicados.")

    if df_produto["id_produto"].duplicated().any():
        raise ValueError("Existem IDs de produtos duplicados.")

    # Identificar clientes e produtos inexistentes
    if (~df_venda["id_cliente"].isin(df_cliente["id_cliente"])).any():
        raise ValueError("Existem vendas com clientes inexistentes.")

    if (~df_venda["id_produto"].isin(df_produto["id_produto"])).any():
        raise ValueError("Existem vendas com produtos inexistentes.")

    # Validar os relacionamentos durante as junções
    df_final = df_venda.merge(
        df_cliente, on="id_cliente", how="left", validate="many_to_one"
    )
    df_final = df_final.merge(
        df_produto, on="id_produto", how="left", validate="many_to_one"
    )

    df_final.to_csv(processed_dir / "vendas_integradas.csv", index=False, encoding="utf-8")

    logger.info("Integração concluída: %d registros", len(df_final))
    return len(df_final)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    integrar_dados()
