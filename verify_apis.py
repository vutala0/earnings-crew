"""
Verify all three external dependencies before we build on them.

Tests:
1. Finnhub earnings endpoint - returns historical EPS surprise data
2. Twelve Data time series endpoint - returns daily price history (for market-outcome eval)
3. Gemini classification call - confirms the LLM API is reachable
"""

import os
from dotenv import load_dotenv
import finnhub
from twelvedata import TDClient
from google import genai

load_dotenv()

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")
TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("API VERIFICATION")
print("=" * 60)

# --- 1. Finnhub: earnings ---
print("\n[1/3] Finnhub earnings endpoint...")
try:
    finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)
    earnings = finnhub_client.company_earnings("AAPL", limit=4)
    print(f"  OK -- got {len(earnings)} earnings records for AAPL")
    print(f"  Most recent: {earnings[0]}")
except Exception as e:
    print(f"  FAILED: {e}")

# --- 2. Twelve Data: price history ---
print("\n[2/3] Twelve Data time series endpoint...")
try:
    td = TDClient(apikey=TWELVE_DATA_KEY)
    ts = td.time_series(
        symbol="AAPL",
        interval="1day",
        outputsize=30,
    ).as_json()
    print(f"  OK -- got {len(ts)} daily bars for AAPL")
    print(f"  Most recent bar: {ts[0]}")
except Exception as e:
    print(f"  FAILED: {e}")

# --- 3. Gemini: classification call ---
print("\n[3/3] Gemini API...")
try:
    client = genai.Client(api_key=GEMINI_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Respond with exactly one word: bullish, bearish, or neutral. "
            "Headline: Apple beats Q3 earnings, raises full-year guidance."
        ),
    )
    print(f"  OK -- Gemini returned: {response.text.strip()}")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)