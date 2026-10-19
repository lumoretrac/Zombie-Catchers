#!/usr/bin/env python3
"""Build the game data and item icon sheet for ARC Raiders Utility.

Reads a local clone of the community data repo
https://github.com/RaidTheory/arcraiders-data (MIT) and writes:

  arc-utility/game.json   compact English-only data the app loads
  arc-utility/icons.webp  every item icon in one sprite sheet

Usage:
  git clone --depth 1 https://github.com/RaidTheory/arcraiders-data /path/to/arcraiders-data
  python3 tools/build_arc_data.py /path/to/arcraiders-data

Then republish the artifact so the new files go live.
"""
import glob
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone

from PIL import Image

CELL = 64
COLS = 24
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'arc-utility')


def en(v):
    """Pick the English string out of a localized field."""
    if isinstance(v, dict):
        return v.get('en') or next(iter(v.values()), '')
    return v or ''


def pairs(reqs, key='itemId'):
    return [[r[key], r['quantity']] for r in (reqs or []) if r.get(key)]


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def git(src, *args):
    try:
        return subprocess.check_output(['git', '-C', src, *args], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def build(src):
    items = {}
    for path in sorted(glob.glob(os.path.join(src, 'items', '*.json'))):
        j = load(path)
        it = {
            'n': en(j.get('name')),
            't': j.get('type') or 'Misc',
            'r': j.get('rarity') or 'Common',
            'v': j.get('value') or 0,
            's': j.get('stackSize') or 1,
        }
        if j.get('weightKg') is not None:
            it['w'] = j['weightKg']
        desc = en(j.get('description'))
        if desc:
            it['d'] = desc
        if j.get('foundIn'):
            it['f'] = [s.strip() for s in j['foundIn'].split(',') if s.strip()]
        for src_key, dst_key in (('recyclesInto', 'rc'), ('salvagesInto', 'sv'), ('recipe', 'rp')):
            if j.get(src_key):
                it[dst_key] = j[src_key]
        if j.get('craftBench'):
            cb = j['craftBench']
            it['cb'] = cb if isinstance(cb, str) else cb[0]
            it['sl'] = j.get('stationLevelRequired') or 1
        if j.get('craftQuantity'):
            it['cq'] = j['craftQuantity']
        if j.get('questItem'):
            it['q'] = 1
        if j.get('blueprintLocked'):
            it['bp'] = 1
        if j.get('isWeapon'):
            it['wp'] = 1
        if j.get('vendors'):
            it['vd'] = [
                {'tr': v.get('trader'), 'c': v.get('cost') or {}, 'lim': v.get('limit')}
                for v in j['vendors'] if v.get('trader')
            ]
        items[j['id']] = it

    quests = []
    for path in sorted(glob.glob(os.path.join(src, 'quests', '*.json'))):
        j = load(path)
        quests.append({
            'id': j['id'],
            'n': en(j.get('name')),
            'tr': j.get('trader') or 'Unknown',
            'm': j.get('map') or [],
            'o': [en(o) for o in j.get('objectives') or []],
            'req': pairs(j.get('requiredItemIds')),
            'rew': pairs(j.get('rewardItemIds')),
            'g': pairs(j.get('grantedItemIds')),
            'p': j.get('previousQuestIds') or [],
            'x': j.get('nextQuestIds') or [],
            'or': [en(o) for o in j.get('otherRequirements') or []],
            'one': bool(j.get('objectivesOneRound')),
        })

    benches = []
    for path in sorted(glob.glob(os.path.join(src, 'hideout', '*.json'))):
        j = load(path)
        if not j.get('levels'):
            continue
        benches.append({
            'id': j['id'],
            'n': en(j.get('name')),
            'max': j.get('maxLevel') or len(j['levels']),
            'lv': [{
                'l': lv['level'],
                'req': pairs(lv.get('requirementItemIds')),
                'or': [en(o) for o in lv.get('otherRequirements') or []],
                'd': en(lv.get('description')),
            } for lv in j['levels']],
        })

    projects = []
    for j in load(os.path.join(src, 'projects.json')):
        if j.get('disabled'):
            continue
        projects.append({
            'id': j['id'],
            'n': en(j.get('name')),
            'd': en(j.get('description')),
            'start': j.get('startDate'),
            'end': j.get('endDate'),
            'ph': [{
                'n': en(ph.get('name')),
                'd': en(ph.get('description')),
                'req': pairs(ph.get('requirementItemIds')),
            } for ph in j.get('phases') or []],
        })

    bots = [{
        'id': b['id'],
        'n': en(b.get('name')),
        'type': en(b.get('type')),
        'threat': b.get('threat'),
        'maps': b.get('maps') or [],
        'drops': b.get('drops') or [],
        'weak': en(b.get('weakness')),
    } for b in load(os.path.join(src, 'bots.json'))]

    trades = [{
        'tr': t['trader'],
        'id': t['itemId'],
        'q': t.get('quantity') or 1,
        'cost': [t['cost']['itemId'], t['cost']['quantity']] if t.get('cost') else None,
        'lim': t.get('dailyLimit'),
    } for t in load(os.path.join(src, 'trades.json'))]

    maps = [{'id': m['id'], 'n': en(m.get('name'))} for m in load(os.path.join(src, 'maps.json'))]

    # Icon sheet: one 64px cell per item, in item-id order.
    with_icon = [i for i in sorted(items) if os.path.exists(os.path.join(src, 'images', 'items', i + '.png'))]
    rows = math.ceil(len(with_icon) / COLS)
    sheet = Image.new('RGBA', (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for idx, item_id in enumerate(with_icon):
        im = Image.open(os.path.join(src, 'images', 'items', item_id + '.png')).convert('RGBA')
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        x = (idx % COLS) * CELL + (CELL - im.width) // 2
        y = (idx // COLS) * CELL + (CELL - im.height) // 2
        sheet.paste(im, (x, y), im)
        items[item_id]['i'] = idx

    commit = git(src, 'rev-parse', '--short', 'HEAD')
    commit_date = git(src, 'log', '-1', '--format=%cI')
    data = {
        'meta': {
            'source': 'https://github.com/RaidTheory/arcraiders-data',
            'site': 'https://arctracker.io',
            'commit': commit,
            'commitDate': commit_date,
            'builtAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'iconCell': CELL,
            'iconCols': COLS,
            'iconRows': rows,
        },
        'items': items,
        'quests': quests,
        'benches': benches,
        'projects': projects,
        'bots': bots,
        'trades': trades,
        'maps': maps,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'game.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    sheet.save(os.path.join(OUT_DIR, 'icons.webp'), 'WEBP', quality=82, method=6)
    print(f'{len(items)} items ({len(with_icon)} with icons), {len(quests)} quests, '
          f'{len(benches)} benches, {len(projects)} projects, {len(bots)} ARC, {len(trades)} trades')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(os.path.abspath(sys.argv[1]))
