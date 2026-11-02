#!/usr/bin/env python3
"""Best-seller lists from Shopify stores, read through the "Shopify Best Sellers" actor on Apify.

    APIFY_TOKEN=<your token> python3 best_sellers.py https://deathwishcoffee.com https://allbirds.com

Python 3.9 or newer, standard library only. Prints each list and writes best-sellers.csv.
Optional settings:
    TOP=50                                how far down each list to read (default 20)
    OUT=my-file.csv                       where to save the CSV
    COLLECTIONS=most-popular,new-arrivals read these collections instead of finding the bestseller list
"""
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ACTOR = "tidyfeed~shopify-best-sellers"
# Only change this to point the script at a test server.
API = os.environ.get("APIFY_API_BASE_URL") or "https://api.apify.com"
COLUMNS = [
    "storeDomain", "collectionTitle", "rank", "productTitle", "vendor", "productType",
    "minPrice", "maxPrice", "maxCompareAtPrice", "discountPercent", "onSale", "anyAvailable", "productUrl",
]


def host(url):
    """The actor names each store by its host name, so match the addresses given on the command line the same way."""
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return urlsplit(url).hostname or url


def cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def main():
    token = os.environ.get("APIFY_TOKEN")
    stores = sys.argv[1:]
    out = os.environ.get("OUT") or "best-sellers.csv"
    collections = [c.strip() for c in (os.environ.get("COLLECTIONS") or "").split(",") if c.strip()]
    if not token or not stores:
        sys.exit("Usage: APIFY_TOKEN=<your Apify API token> python3 best_sellers.py <store URL> [<store URL> ...]\n"
                 "Your token is at https://console.apify.com/settings/integrations")
    try:
        top = int(os.environ.get("TOP") or 20)
    except ValueError:
        top = 0
    if not 1 <= top <= 5000:
        sys.exit("TOP must be a whole number from 1 to 5000.")

    payload = {"storeUrls": stores, "maxCollectionsPerStore": 1, "maxProductsPerCollection": top}
    if collections:
        payload["collectionHandles"] = collections

    print(f"Reading {len(stores)} store(s) — usually a few seconds per store...")
    request = urllib.request.Request(
        f"{API}/v2/acts/{ACTOR}/run-sync-get-dataset-items",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=330) as response:
            rows = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            message = json.loads(body)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = body[:300]
        if error.code == 408:
            message = ("the run took longer than 5 minutes to finish. Check it in your Apify Console, "
                       "and pass fewer stores per call.")
        sys.exit(f"Apify returned HTTP {error.code}: {message}")
    except urllib.error.URLError as error:
        sys.exit(f"Could not reach Apify: {error.reason}")

    for store in dict.fromkeys(host(s) for s in stores):
        found = [r for r in rows if r.get("storeDomain") == store]
        if not found:
            print(f"\n{store}: no ranked products — the store may publish no bestseller collection "
                  "(the run in your Apify Console says why).")
            continue
        collection = None
        for r in found:
            if r["collectionTitle"] != collection:
                collection = r["collectionTitle"]
                print(f'\n{store} — "{collection}"')
            price = f"{r['minPrice']}" if r["minPrice"] == r["maxPrice"] else f"{r['minPrice']}–{r['maxPrice']}"
            notes = []
            if r.get("onSale"):
                notes.append(f"{r['discountPercent']}% off")
            if r.get("anyAvailable") is False:
                notes.append("sold out")
            extra = f"  ({', '.join(notes)})" if notes else ""
            print(f"{r['rank']:>4}  {r['productTitle']}  {price}{extra}")

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COLUMNS)
        for r in rows:
            writer.writerow([cell(r.get(c)) for c in COLUMNS])
    print(f"\nSaved {len(rows)} row(s) to {out}")


if __name__ == "__main__":
    main()
