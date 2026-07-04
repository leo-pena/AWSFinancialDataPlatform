import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
S3_BUCKET = "aws-financial-data-platform-leopena"

SYMBOLS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]

BASE_URL = "https://finnhub.io/api/v1/stock/profile2"

INGESTION_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

LOCAL_OUTPUT_DIR = (
    Path("data/raw/finnhub/company_profiles")
    / f"ingestion_date={INGESTION_DATE}"
)

S3_PREFIX = f"raw/finnhub/company_profiles/ingestion_date={INGESTION_DATE}"

s3_client = boto3.client("s3")


def fetch_company_profile(symbol):
    params = {
        "symbol": symbol,
        "token": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def save_json_locally(data, symbol):
    symbol_dir = LOCAL_OUTPUT_DIR / f"symbol={symbol}"
    symbol_dir.mkdir(parents=True, exist_ok=True)

    output_file = symbol_dir / "profile.json"

    with open(output_file, "w") as file:
        json.dump(data, file, indent=2)

    print(f"Saved local file: {output_file}")

    return output_file


def upload_to_s3(local_file, symbol):
    s3_key = f"{S3_PREFIX}/symbol={symbol}/profile.json"

    s3_client.upload_file(
        Filename=str(local_file),
        Bucket=S3_BUCKET,
        Key=s3_key,
    )

    print(f"Uploaded to S3: s3://{S3_BUCKET}/{s3_key}")


def main():
    if not API_KEY:
        raise ValueError("FINNHUB_API_KEY is missing. Check your .env file.")

    for symbol in SYMBOLS:
        profile = fetch_company_profile(symbol)
        local_file = save_json_locally(profile, symbol)
        upload_to_s3(local_file, symbol)


if __name__ == "__main__":
    main()