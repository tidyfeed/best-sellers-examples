#!/usr/bin/env python3
"""Compare two best-seller snapshots written by best_sellers.py or best-sellers.mjs.

    python3 compare_snapshots.py last-week.csv this-week.csv

Prints, list by list, what entered, what moved and what dropped out.
Python 3.9 or newer, standard library only.
"""
import csv
import sys


def load(path):
    """{(store, collection): {product URL: (rank, title)}}"""
    lists = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = (row["storeDomain"], row["collectionTitle"])
            lists.setdefault(key, {})[row["productUrl"]] = (int(row["rank"]), row["productTitle"])
    return lists


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 compare_snapshots.py <older.csv> <newer.csv>")
    before, after = load(sys.argv[1]), load(sys.argv[2])

    for store, collection in sorted(set(before) | set(after)):
        old = before.get((store, collection), {})
        new = after.get((store, collection), {})
        entered = sorted(new[url] for url in new.keys() - old.keys())
        moved = sorted((new[url][0], old[url][0], new[url][1]) for url in new.keys() & old.keys() if new[url][0] != old[url][0])
        dropped = sorted(old[url] for url in old.keys() - new.keys())

        print(f'\n{store} — "{collection}"')
        if not (entered or moved or dropped):
            print("  no change")
            continue
        for rank, title in entered:
            print(f"  new   #{rank}  {title}")
        for now, was, title in moved:
            print(f"  {'up' if now < was else 'down':<4}  #{was} -> #{now}  {title}")
        for rank, title in dropped:
            print(f"  gone  was #{rank}  {title}")


if __name__ == "__main__":
    main()
