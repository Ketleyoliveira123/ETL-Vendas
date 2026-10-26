import logging # serve para registrar mensagens de log durante a execução do ETL
from clean_data import limpar_dados
from merge_data import integrar_dados
from load_data import carregar_dados
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent 
LOG_DIR = BASE_DIR / "logs" 

def executar_etl():
    try:
        logging.info("Iniciando o ETL")

        limpar_dados()
        logging.info("Limpeza concluída")

        integrar_dados()
        logging.info("Integração concluída")

        carregar_dados()
        logging.info("Carga no banco concluída")

        logging.info("ETL finalizado com sucesso")

    except Exception as erro:
        logging.error(f"Erro durante o ETL: {erro}")
        raise

if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=str(LOG_DIR / "etl.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    executar_etl()



