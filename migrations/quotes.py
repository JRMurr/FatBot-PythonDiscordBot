#!/usr/bin/env python3

import argparse
import json
from pymongo import MongoClient

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', default='quotes.json',
                        help='File to load old quotes data from')
    parser.add_argument('--host', default='mongodb://db:27017')
    parser.add_argument('--db', '-d', default='fatbot',
                        help='Mongo DB name')
    args = parser.parse_args()

    db = MongoClient(args.host)[args.db]
    coll = db.quotes

    with open(args.file) as f:
        quotes = json.load(f)
    print(f'Inserting {len(quotes)} quotes...')
    for quote, source in quotes:
        coll.insert_one({'quote': quote, 'source': source})
    print('Done!')
