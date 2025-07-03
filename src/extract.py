import os, json, requests, uuid, argparse
from datetime import datetime, timezone
from collections import defaultdict
from src.utils import daterange

API_URL = "https://api.openbrewerydb.org/v1/breweries"
DATA_DIR = os.getenv("DATA_DIR", "/data/bronze/breweries")
PAGE_SIZE = 200
N_PARTITIONS = 40

def fetch_breweries(start_date=None, end_date=None, **_):
    if not start_date:
        start_date = end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not end_date:
        end_date = start_date

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    print(f"[extract.py] Fetching from {start_dt} to {end_dt}...")

    for day in daterange(start_dt, end_dt):
        dt_str = day.strftime("%Y-%m-%d")
        breweries_by_state = defaultdict(list)
        page = 1
        while True:
            resp = requests.get(API_URL, params={"page": page, "per_page": PAGE_SIZE}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            for brewery in data:
                state = brewery.get("state") or "unknown"
                breweries_by_state[state].append(brewery)
            page += 1

        for state, breweries in breweries_by_state.items():
            for part in range(0, len(breweries), max(1, len(breweries)//N_PARTITIONS + 1)):
                sublist = breweries[part:part + N_PARTITIONS]
                part_idx = part // N_PARTITIONS
                out_dir = f"{DATA_DIR}/state={state}/dt={dt_str}"
                os.makedirs(out_dir, exist_ok=True)
                fname = f"breweries_{state}_p{part_idx}_{uuid.uuid4().hex}.json"
                with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                    json.dump(sublist, f, ensure_ascii=False)
        print(f"[extract.py] Dia {dt_str}: {sum(len(x) for x in breweries_by_state.values())} registros salvos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date", type=str, help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, help="Data final (YYYY-MM-DD)")
    args = parser.parse_args()
    fetch_breweries(start_date=args.start_date, end_date=args.end_date)
