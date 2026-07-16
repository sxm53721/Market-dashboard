import json
import os
import datetime
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

BASE = "https://polling.finance.naver.com/api/realtime"

GROUPS = {
    "domesticIndex": f"{BASE}/domestic/index/KOSPI,KOSDAQ",
    "worldIndex": f"{BASE}/worldstock/index/.DJI,.IXIC,.SPX,.INX,.GSPC",
    "usStocks": f"{BASE}/worldstock/stock/AAPL.O,MSFT.O,GOOG.O,AMZN.O,NVDA.O,META.O,TSLA.O",
    "krStocks": f"{BASE}/domestic/stock/005930,000660",
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data.json")


def load_previous():
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def fetch_group(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("datas", [])


def main():
    previous = load_previous()
    result = {}
    errors = {}

    for key, url in GROUPS.items():
        try:
            result[key] = fetch_group(url)
        except Exception as e:
            # 실패한 그룹은 이전 값을 유지해서, 일시적 오류로 데이터가 통째로
            # 사라지지 않도록 함
            result[key] = previous.get(key, [])
            errors[key] = str(e)

    kst = datetime.timezone(datetime.timedelta(hours=9))
    output = {
        "updatedAt": datetime.datetime.now(kst).isoformat(),
        **result,
    }
    if errors:
        output["errors"] = errors

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUTPUT_PATH}")
    if errors:
        print("Some groups failed and used cached data:", errors)


if __name__ == "__main__":
    main()
