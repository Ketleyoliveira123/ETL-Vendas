import logging
from pathlib import Path

from .clean_data import limpar_dados
from .load_data import carregar_dados
from .merge_data import integrar_dados

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

logger = logging.getLogger(__name__)


def executar_etl():
    try:
        logger.info("Iniciando o ETL")
        limpar_dados()
        integrar_dados()
        carregar_dados()
        logger.info("ETL finalizado com sucesso")
    except Exception:
        logger.exception("Erro durante o ETL")
        raise


def configurar_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


if __name__ == "__main__":
    configurar_logging()
    executar_etl()
