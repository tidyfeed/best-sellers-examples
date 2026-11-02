#!/usr/bin/env node
// Best-seller lists from Shopify stores, read through the "Shopify Best Sellers" actor on Apify.
//
//   APIFY_TOKEN=<your token> node best-sellers.mjs https://deathwishcoffee.com https://allbirds.com
//
// Node.js 18 or newer, nothing to install. Prints each list and writes best-sellers.csv.
// Optional settings:
//   TOP=50                               how far down each list to read (default 20)
//   OUT=my-file.csv                      where to save the CSV
//   COLLECTIONS=most-popular,new-arrivals read these collections instead of finding the bestseller list

import { writeFileSync } from 'node:fs';

const ACTOR = 'tidyfeed~shopify-best-sellers';
// Only change this to point the script at a test server.
const API = process.env.APIFY_API_BASE_URL || 'https://api.apify.com';
const COLUMNS = [
    'storeDomain', 'collectionTitle', 'rank', 'productTitle', 'vendor', 'productType',
    'minPrice', 'maxPrice', 'maxCompareAtPrice', 'discountPercent', 'onSale', 'anyAvailable', 'productUrl',
];

const token = process.env.APIFY_TOKEN;
const stores = process.argv.slice(2);
const top = Number(process.env.TOP || 20);
const out = process.env.OUT || 'best-sellers.csv';
const collections = (process.env.COLLECTIONS || '').split(',').map((s) => s.trim()).filter(Boolean);

if (!token || stores.length === 0) {
    console.error('Usage: APIFY_TOKEN=<your Apify API token> node best-sellers.mjs <store URL> [<store URL> ...]');
    console.error('Your token is at https://console.apify.com/settings/integrations');
    process.exit(1);
}
if (!Number.isInteger(top) || top < 1 || top > 5000) {
    console.error('TOP must be a whole number from 1 to 5000.');
    process.exit(1);
}

const input = { storeUrls: stores, maxCollectionsPerStore: 1, maxProductsPerCollection: top };
if (collections.length) input.collectionHandles = collections;

console.log(`Reading ${stores.length} store(s) — usually a few seconds per store...`);
let response;
try {
    response = await fetch(`${API}/v2/acts/${ACTOR}/run-sync-get-dataset-items`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
    });
} catch (error) {
    console.error(`Could not reach Apify: ${error.cause?.code ?? error.message}`);
    process.exit(1);
}
if (!response.ok) {
    const body = await response.text();
    let message = body.slice(0, 300);
    try {
        message = JSON.parse(body).error?.message ?? message;
    } catch {
        // not JSON — keep the raw text
    }
    if (response.status === 408) {
        message = 'the run took longer than 5 minutes to finish. Check it in your Apify Console, and pass fewer stores per call.';
    }
    console.error(`Apify returned HTTP ${response.status}: ${message}`);
    process.exit(1);
}
const rows = await response.json();

// The actor names each store by its host name, so match the addresses given on the command line the same way.
const host = (url) => {
    try {
        return new URL(/^https?:\/\//i.test(url) ? url : `https://${url}`).hostname;
    } catch {
        return url;
    }
};
for (const store of new Set(stores.map(host))) {
    const list = rows.filter((r) => r.storeDomain === store);
    if (!list.length) {
        console.log(`\n${store}: no ranked products — the store may publish no bestseller collection (the run in your Apify Console says why).`);
        continue;
    }
    let collection;
    for (const r of list) {
        if (r.collectionTitle !== collection) {
            collection = r.collectionTitle;
            console.log(`\n${store} — "${collection}"`);
        }
        const price = r.minPrice === r.maxPrice ? `${r.minPrice}` : `${r.minPrice}–${r.maxPrice}`;
        const notes = [r.onSale && `${r.discountPercent}% off`, r.anyAvailable === false && 'sold out'].filter(Boolean);
        console.log(`${String(r.rank).padStart(4)}  ${r.productTitle}  ${price}${notes.length ? `  (${notes.join(', ')})` : ''}`);
    }
}

const cell = (value) => {
    if (value === null || value === undefined) return '';
    const s = String(value);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
writeFileSync(out, [COLUMNS.join(','), ...rows.map((r) => COLUMNS.map((c) => cell(r[c])).join(','))].join('\n') + '\n');
console.log(`\nSaved ${rows.length} row(s) to ${out}`);
