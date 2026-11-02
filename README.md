# Best sellers from any Shopify store — Node.js & Python examples

Get a Shopify store's bestseller list in the order the store itself ranks it — rank, price, discount and stock for every product — as CSV or JSON.

These small scripts call the [**Shopify Best Sellers**](https://apify.com/tidyfeed/shopify-best-sellers) actor on Apify. You don't need a Shopify login, API key or partner account, only an Apify account. The scripts have no dependencies.

Prefer not to code? Open the [actor page](https://apify.com/tidyfeed/shopify-best-sellers) and press Start — the input comes pre-filled.

*Maintained by [tidyfeed](https://apify.com/tidyfeed), the developer of the actor.*

## What you get

The top of deathwishcoffee.com's Best Sellers collection, read on 2 November 2026:

| rank | product | price | on sale | in stock |
|---:|---|---|---|---|
| 1 | Pumpkin Chai Coffee | 13.99–69.95 | no | yes |
| 2 | Pumpkin Chai Single-Serve Pods | 12.99–38.97 | no | yes |
| 3 | White Chocolate Pistachio Coffee | 13.99–69.95 | no | yes |
| 4 | Maple Cinnamon Coffee | 13.99–69.95 | no | yes |
| 5 | Power Surge Coffee | 19.99–84.99 | no | yes |

The scripts save `storeDomain`, `collectionTitle`, `rank`, `productTitle`, `vendor`, `productType`, `minPrice`, `maxPrice`, `maxCompareAtPrice`, `discountPercent`, `onSale`, `anyAvailable` and `productUrl` — see [`sample-output/`](sample-output/deathwishcoffee-best-sellers.csv). Called directly, the actor also returns tags, SKUs, images, variant counts and publish dates.

Finding the right collection is the hard part. Stores name and address their bestseller lists differently — in September 2026 Gymshark's "Best Sellers" lived at `/collections/most-popular` — and many keep test or internal collections next to the real one. The actor reads each store's own collection list and picks the real bestseller list.

## Quick start

1. Create an Apify account and copy your API token from **Console → Settings → [API & Integrations](https://console.apify.com/settings/integrations)**.
2. Run one of these.

**curl**

```bash
curl -X POST "https://api.apify.com/v2/acts/tidyfeed~shopify-best-sellers/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"storeUrls": ["https://deathwishcoffee.com"], "maxCollectionsPerStore": 1, "maxProductsPerCollection": 20}'
```

**Node.js 18+**

```bash
export APIFY_TOKEN=your_token
node node/best-sellers.mjs https://deathwishcoffee.com https://allbirds.com
```

**Python 3.9+**

```bash
export APIFY_TOKEN=your_token
python3 python/best_sellers.py https://deathwishcoffee.com https://allbirds.com
```

Both scripts print each list and save `best-sellers.csv`. Optional settings:

| Setting | Default | What it does |
|---|---|---|
| `TOP` | 20 | How far down each list to read (1–5000) |
| `OUT` | `best-sellers.csv` | Where to save the CSV |
| `COLLECTIONS` | — | Comma-separated collection handles to read instead, e.g. `most-popular,new-arrivals` |

Each call waits for the run to finish. If a run takes longer than 5 minutes (many stores, deep lists), Apify answers HTTP 408 — check the run in your Apify Console and pass fewer stores per call.

## Track changes week over week

```bash
OUT=week-44.csv python3 python/best_sellers.py https://deathwishcoffee.com https://allbirds.com
# a week later
OUT=week-45.csv python3 python/best_sellers.py https://deathwishcoffee.com https://allbirds.com
python3 python/compare_snapshots.py week-44.csv week-45.csv
```

It prints what entered each list, what moved and what dropped out. Example output, from a test with an edited snapshot:

```
deathwishcoffee.com — "Best Sellers"
  new   #10  Brand New Blend
  up    #2 -> #1  Pumpkin Chai Single-Serve Pods
  down  #1 -> #2  Pumpkin Chai Coffee
  gone  was #10  Dark Roast Single-Serve Pods
```

To run it without your own machine, give the actor a [schedule on Apify](https://docs.apify.com/platform/schedules) and export each run's dataset as CSV.

## What it costs

The actor charges per ranked product delivered: **$10.00 per 1,000 products plus $0.005 per run** on Apify's free plan, with 10–30% off on paid plans. The top 20 of one store comes to about $0.21; the top 20 of ten stores, about $2.01. A store with no bestseller collection returns nothing and costs nothing beyond the run start. The [actor page](https://apify.com/tidyfeed/shopify-best-sellers) has current prices.

## Honest limits

- `rank` is the order the store publishes, not units sold. Shopify does not publish sales figures to anyone.
- Stores that list each colour as its own product repeat the same style in their list (one shoe in five shades). The rows are kept as the store lists them.
- Stock is the store's in-stock flag as seen from the United States. Currency isn't in the feed, so prices are plain numbers in the store's own currency.
- Some stores publish no bestseller collection. The scripts say so, and `COLLECTIONS` lets you point them at a collection yourself.
- Password-protected and pre-launch stores return nothing.

## Questions

GitHub issues are turned off for this repository. Questions and bug reports go to the actor's [Issues tab on Apify](https://apify.com/tidyfeed/shopify-best-sellers/issues), where they are read and answered.

## License

Code: [MIT](LICENSE). Use the data responsibly and in line with each store's terms.

Shopify is a trademark of Shopify Inc. This project is not affiliated with, endorsed by, or sponsored by Shopify.
