#!/usr/bin/env python3
"""Build the game data, item icon sheet and map tiles for ARC Raiders Utility.

Reads a local clone of the community data repo
https://github.com/RaidTheory/arcraiders-data (MIT) and writes:

  arc-utility/game.json   compact English-only data the app loads
  arc-utility/icons.webp  every item icon in one sprite sheet
  arc-utility/bots/       one picture per ARC enemy
  arc-utility/maps/       map tiles, 1000 px square, three zoom levels
                          (generated, not committed: rerun this script)

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
TILE = 1000          # tile edge in px; the map is 1000 units wide, so zoom z is 1000 * 2^z px wide
MAX_Z = 2            # zoom 2 = 4000 px wide, the sharpest level we ship

# Map groups shown in the app. Each layer is one floor or view, keyed by the map id quests and ARC use.
# 'src' is either a single annotated PNG (area names, loot zones, extracts) or a v2 tile pyramid.
ATLAS = [
    ('dam_battlegrounds', 'Dam Battlegrounds', [('dam_battlegrounds', '', 'png', 'legacy/dam_battlegrounds.png')]),
    ('buried_city', 'Buried City', [('buried_city', '', 'png', 'legacy/buried_city.png')]),
    ('the_spaceport', 'The Spaceport', [('the_spaceport', '', 'png', 'legacy/the_spaceport.png')]),
    ('the_blue_gate', 'The Blue Gate', [('the_blue_gate', '', 'png', 'legacy/the_blue_gate.png')]),
    ('stella_montis', 'Stella Montis', [
        ('stella_montis_upper', 'Upper', 'png', 'stella_montis_upper.png'),
        ('stella_montis_lower', 'Lower', 'png', 'stella_montis_lower.png'),
    ]),
    ('riven_tides', 'Riven Tides', [('riven_tides', '', 'v2', 'riven-tides/v2/high/2')]),
]
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
        effects = {k: v['value'] for k, v in (j.get('effects') or {}).items()
                   if isinstance(v, dict) and v.get('value') is not None}
        if effects:
            it['e'] = effects
        if j.get('modSlots'):
            it['ms'] = j['modSlots']
        if j.get('compatibleWith'):
            it['cw'] = j['compatibleWith']
        if j.get('upgradesTo'):
            it['ut'] = j['upgradesTo']
        if j.get('shieldCharge') is not None:
            it['sh'] = {'charge': j['shieldCharge'], 'mitigation': j.get('damageMitigation'), 'speed': j.get('movementSpeedModifier') or 0}
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
                'rew': [rw for r in ph.get('requirementItemIds') or [] for rw in pairs(r.get('rewardItemIds'))],
            } for ph in j.get('phases') or []],
        })

    bots = [{
        'id': b['id'],
        'n': en(b.get('name')),
        'type': en(b.get('type')),
        'threat': b.get('threat'),
        'd': en(b.get('description')),
        'maps': b.get('maps') or [],
        'drops': b.get('drops') or [],
        'weak': en(b.get('weakness')),
        'dx': b.get('destroyXp'),
        'lx': b.get('lootXp'),
    } for b in load(os.path.join(src, 'bots.json'))]
    os.makedirs(os.path.join(OUT_DIR, 'bots'), exist_ok=True)
    for b in bots:
        path = os.path.join(src, 'images', 'bots', b['id'] + '.png')
        if not os.path.exists(path):
            continue
        im = Image.open(path).convert('RGBA')
        if im.width > 640:
            im = im.resize((640, round(640 * im.height / im.width)), Image.LANCZOS)
        im.save(os.path.join(OUT_DIR, 'bots', b['id'] + '.webp'), 'WEBP', quality=80, method=6)
        b['img'] = [im.width, im.height]

    trades = [{
        'tr': t['trader'],
        'id': t['itemId'],
        'q': t.get('quantity') or 1,
        'cost': [t['cost']['itemId'], t['cost']['quantity']] if t.get('cost') else None,
        'lim': t.get('dailyLimit'),
    } for t in load(os.path.join(src, 'trades.json'))]

    maps = [{'id': m['id'], 'n': en(m.get('name'))} for m in load(os.path.join(src, 'maps.json'))]

    events = load(os.path.join(src, 'map-events', 'map-events.json')).get('eventTypes', {})
    conditions = [{'id': k, 'n': e.get('displayName') or k, 'cat': e.get('category')}
                  for k, e in events.items() if k != 'none' and not e.get('disabled')]

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

    atlas = build_maps(src)

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
        'atlas': atlas,
        'conditions': conditions,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'game.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    sheet.save(os.path.join(OUT_DIR, 'icons.webp'), 'WEBP', quality=82, method=6)
    print(f'{len(items)} items ({len(with_icon)} with icons), {len(quests)} quests, '
          f'{len(benches)} benches, {len(projects)} projects, {len(bots)} ARC, {len(trades)} trades')


def load_layer(src, kind, path):
    """Return the layer as one RGB image, MAX_Z level wide (4000 px)."""
    full = TILE * 2 ** MAX_Z
    if kind == 'png':
        im = Image.open(os.path.join(src, 'images', 'maps', path)).convert('RGB')
        return im.resize((full, round(full * im.height / im.width)), Image.LANCZOS)
    # v2 pyramid: zoom 2 of the source is 4000 px square in 512 px tiles named {x}/{y}.webp
    base = os.path.join(src, 'images', 'maps', path)
    im = Image.new('RGB', (4000, 4000))
    for x in sorted(os.listdir(base), key=int):
        for name in os.listdir(os.path.join(base, x)):
            y = int(name.split('.')[0])
            im.paste(Image.open(os.path.join(base, x, name)).convert('RGB'), (int(x) * 512, y * 512))
    return im.resize((full, full), Image.LANCZOS) if full != 4000 else im


def build_maps(src):
    out_root = os.path.join(OUT_DIR, 'maps')
    atlas = []
    for group_id, group_name, layers in ATLAS:
        group = {'id': group_id, 'n': group_name, 'layers': []}
        for layer_id, layer_name, kind, path in layers:
            im = load_layer(src, kind, path)
            levels = []
            for z in range(MAX_Z + 1):
                w = TILE * 2 ** z
                h = round(w * im.height / im.width)
                level = im if z == MAX_Z else im.resize((w, h), Image.LANCZOS)
                nx, ny = math.ceil(w / TILE), math.ceil(h / TILE)
                os.makedirs(os.path.join(out_root, layer_id, str(z)), exist_ok=True)
                for x in range(nx):
                    for y in range(ny):
                        tile = Image.new('RGB', (TILE, TILE), (14, 12, 10))
                        tile.paste(level.crop((x * TILE, y * TILE, min(w, (x + 1) * TILE), min(h, (y + 1) * TILE))), (0, 0))
                        tile.save(os.path.join(out_root, layer_id, str(z), f'{x}_{y}.webp'), 'WEBP', quality=74, method=6)
                levels.append([nx, ny])
            group['layers'].append({
                'id': layer_id, 'n': layer_name, 'style': 'labeled' if kind == 'png' else 'satellite',
                'w': 1000, 'h': round(1000 * im.height / im.width), 'z': levels,
            })
        atlas.append(group)
    return atlas


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(os.path.abspath(sys.argv[1]))
