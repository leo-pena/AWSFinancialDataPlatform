import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")

SYMBOLS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]

BASE_URL = "https://finnhub.io/api/v1/stock/profile2"

INGESTION_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

OUTPUT_DIR = Path("data/raw/finnhub/company_profiles") / f"ingestion_date={INGESTION_DATE}"


def fetch_company_profile(symbol):
    params = {
        "symbol": symbol,
        "token": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def save_json(data, symbol):
    symbol_dir = OUTPUT_DIR / f"symbol={symbol}"
    symbol_dir.mkdir(parents=True, exist_ok=True)

    output_file = symbol_dir / "profile.json"

    with open(output_file, "w") as file:
        json.dump(data, file, indent=2)

    print(f"Saved {symbol} profile to {output_file}")


def main():
    if not API_KEY:
        raise ValueError("FINNHUB_API_KEY is missing. Check your .env file.")

    for symbol in SYMBOLS:
        profile = fetch_company_profile(symbol)
        save_json(profile, symbol)


if __name__ == "__main__":
    main()