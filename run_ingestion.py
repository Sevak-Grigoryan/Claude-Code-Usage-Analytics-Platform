import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TELEMETRY_FILE, EMPLOYEES_FILE
from src.database.connection import initialize_database
from src.ingestion.loader import load_employees, load_telemetry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing database...")
    initialize_database()

    logger.info("Loading employees from %s", EMPLOYEES_FILE)
    emp_count = load_employees(EMPLOYEES_FILE)
    logger.info("Loaded %d employees", emp_count)

    logger.info("Loading telemetry from %s", TELEMETRY_FILE)
    summary = load_telemetry(TELEMETRY_FILE)

    logger.info("Ingestion Summary:")
    logger.info(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
