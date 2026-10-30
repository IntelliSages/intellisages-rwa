"""Dedicated single-instance worker for scheduled CoinGecko RWA market refreshes.

Run as a persistent background process, separate from API replicas:
    python -m app.providers.coingecko_refresh_worker
"""

import logging
import os
import time

from app.database import SessionLocal
from app.providers.coingecko_market_data import refresh_coingecko_rwa_market_data

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("coingecko-refresh-worker")


def run_once() -> None:
    db = SessionLocal()
    try:
        result = refresh_coingecko_rwa_market_data(db)
        logger.info(
            "CoinGecko RWA refresh finished: run_id=%s status=%s coverage=%s",
            result["id"],
            result["status"],
            result["coverage"],
        )
    except Exception:
        logger.exception("CoinGecko RWA refresh could not start.")
    finally:
        db.close()


def main() -> None:
    if not os.getenv("COINGECKO_API_KEY"):
        raise RuntimeError("COINGECKO_API_KEY must be configured for the refresh worker.")
    interval = int(os.getenv("COINGECKO_REFRESH_INTERVAL_SECONDS", "300"))
    if interval < 60:
        raise ValueError("COINGECKO_REFRESH_INTERVAL_SECONDS must be at least 60.")
    logger.info("Starting CoinGecko RWA refresh worker; interval_seconds=%s", interval)
    while True:
        run_once()
        time.sleep(interval)


if __name__ == "__main__":
    main()
