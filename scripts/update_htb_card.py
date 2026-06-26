#!/usr/bin/env python3
from __future__ import annotations
import html, json, os, re, sys, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'htb'
OUT_DIR.mkdir(exist_ok=True)

@dataclass
class HTBProfile:
    user_id: str
    username: str = 'Unknown'
    rank: str = 'N/A'
    country: str = ''
    respect: str = 'N/A'
    points: str = 'N/A'
    user_owns: str = 'N/A'
    system_owns: str = 'N/A'
    challenges: str = 'N/A'
    user_bloods: str = 'N/A'
    system_bloods: str = 'N/A'
    profile_url: str = ''
    updated_at: str = ''
    def normalize(self):
        self.profile_url = self.profile_url or f'https://app.hackthebox.com/public/users/{self.user_id}'
        self.updated_at = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())
        return self

def clean(v: Any, default='N/A') -> str:
    if v in (None, '', []): return default
    if isinstance(v, (int, float)): return f'{v:,}'
    return str(v).strip() or default

def pick(d: dict[str, Any], *keys, default='N/A'):
    for k in keys:
        if k in d and d[k] not in (None, '', []): return clean(d[k], default)
    return default

def flatten(x):
    if not isinstance(x, dict): return {}
    out = dict(x)
    for k in ('profile','user','info','data'):
        if isinstance(x.get(k), dict): out.update(x[k])
    return out

def fetch_with_token(user_id: str, token: str):
    endpoints = [
        f'https://www.hackthebox.com/api/v4/profile/{user_id}',
        f'https://www.hackthebox.com/api/v4/profile/public/{user_id}',
        f'https://www.hackthebox.eu/api/v4/profile/{user_id}',
    ]
    headers = {'Authorization': f'Bearer {token}', 'Accept':'application/json', 'User-Agent':'htb-readme-card'}
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=25)
            if r.status_code in (401,403,404): continue
            r.raise_for_status()
            d = flatten(r.json())
            if not d: continue
            return HTBProfile(
                user_id=user_id,
                username=pick(d,'name','username','user_name','login', default=f'HTB {user_id}'),
                rank=pick(d,'rank','rank_text','rank_name','rank_ownership', default='N/A'),
                country=pick(d,'country','country_name', default=''),
                respect=pick(d,'respect','respects', default='N/A'),
                points=pick(d,'points','rank_points', default='N/A'),
                user_owns=pick(d,'user_owns','user_owns_count','owned_users','owns_user', default='N/A'),
                system_owns=pick(d,'system_owns','system_owns_count','owned_systems','owns_system', default='N/A'),
                challenges=pick(d,'challenge_owns','challenges','challenge_owns_count', default='N/A'),
                user_bloods=pick(d,'user_bloods','user_bloods_count', default='N/A'),
                system_bloods=pick(d,'system_bloods','system_bloods_count', default='N/A'),
                profile_url=f'https://app.hackthebox.com/public/users/{user_id}'
            ).normalize()
        except Exception as e:
            print(f'[token] {url}: {e}', file=sys.stderr)
    return None

def value_after(text, label):
    for p in [rf'{label}\s*[:\-]?\s*([0-9][0-9,.]*)', rf'([0-9][0-9,.]*)\s*{label}']:
        m = re.search(p, text, re.I)
        if m: return m.group(1)
    return 'N/A'

def extract_from_text(user_id, text, url):
    text = re.sub(r'\s+', ' ', text)
    username = f'HTB {user_id}'
    m = re.search(r'@?([A-Za-z0-9_.-]{3,32})\s+(?:Rank|Hacker|Pro Hacker|Elite Hacker|Guru|Omniscient|Script Kiddie)', text)
    if m: username = m.group(1)
    rank = 'N/A'
    for r in ['Omniscient','Guru','Elite Hacker','Pro Hacker','Hacker','Script Kiddie','Noob']:
        if re.search(rf'\b{re.escape(r)}\b', text, re.I):
            rank = r; break
    return HTBProfile(
        user_id=user_id, username=username, rank=rank, profile_url=url,
        respect=value_after(text,'Respect'), points=value_after(text,'Points'),
        user_owns=value_after(text,'User owns|Users owned|User Owns'),
        system_owns=value_after(text,'System owns|Systems owned|Root owns|System Owns'),
        challenges=value_after(text,'Challenges'),
        user_bloods=value_after(text,'User bloods|User Bloods'),
        system_bloods=value_after(text,'System bloods|System Bloods')
    ).normalize()

def scrape_public(user_id):
    url = f'https://app.hackthebox.com/public/users/{user_id}'
    try:
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=25)
        if r.ok:
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text(' ', strip=True)
            nd = soup.find('script', id='__NEXT_DATA__')
            if nd and nd.string: text += ' ' + nd.string
            p = extract_from_text(user_id, text, url)
            if p.username != f'HTB {user_id}' or p.rank != 'N/A': return p
    except Exception as e:
        print(f'[requests scrape] {e}', file=sys.stderr)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(user_agent='Mozilla/5.0')
            page.goto(url, wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(2500)
            text = page.locator('body').inner_text(timeout=10000)
            browser.close()
            return extract_from_text(user_id, text, url)
    except Exception as e:
        print(f'[playwright scrape] {e}', file=sys.stderr)
    return HTBProfile(user_id=user_id, username=f'HTB {user_id}', profile_url=url).normalize()

def esc(s): return html.escape(str(s), quote=True)

def render_svg(p: HTBProfile) -> str:
    bg='#0d1117'; subtle='#181f2b'; text='#f8fafc'; muted='#94a3b8'; purple='#a855f7'; purple2='#c084fc'; green='#9fef00'
    stats=[('Respect',p.respect),('Points',p.points),('User owns',p.user_owns),('System owns',p.system_owns),('Challenges',p.challenges),('User bloods',p.user_bloods),('System bloods',p.system_bloods)]
    boxes=[]
    coords=[(38,154),(196,154),(354,154),(512,154),(38,222),(196,222),(354,222)]
    for (label,val),(x,y) in zip(stats,coords):
        boxes.append(f'<g><rect x="{x}" y="{y}" width="130" height="52" rx="10" fill="{subtle}" stroke="#ffffff18"/><text x="{x+14}" y="{y+21}" fill="{muted}" font-size="11" font-family="Segoe UI,Inter,Arial">{esc(label)}</text><text x="{x+14}" y="{y+42}" fill="{text}" font-size="18" font-weight="700" font-family="Segoe UI,Inter,Arial">{esc(val)}</text></g>')
    return f'''<svg width="680" height="300" viewBox="0 0 680 300" fill="none" xmlns="http://www.w3.org/2000/svg" role="img">
<defs><radialGradient id="orb" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{purple2}" stop-opacity=".75"/><stop offset="55%" stop-color="{purple}" stop-opacity=".28"/><stop offset="100%" stop-color="{purple}" stop-opacity=".05"/></radialGradient><linearGradient id="line" x1="0" y1="0" x2="680" y2="300"><stop stop-color="{purple}"/><stop offset=".55" stop-color="{purple2}"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs>
<rect x="1" y="1" width="678" height="298" rx="18" fill="{bg}" stroke="url(#line)" stroke-width="2"/><circle cx="612" cy="58" r="53" fill="url(#orb)"/><circle cx="612" cy="58" r="23" fill="{purple}" opacity=".28"/>
<text x="38" y="48" fill="{text}" font-size="24" font-weight="800" font-family="Segoe UI,Inter,Arial">Hack The Box Stats</text><text x="38" y="76" fill="{muted}" font-size="12" font-family="Segoe UI,Inter,Arial">{esc(p.profile_url)}</text>
<text x="38" y="112" fill="{green}" font-size="26" font-weight="900" font-family="Segoe UI,Inter,Arial">{esc(p.username)}</text><text x="38" y="138" fill="{text}" font-size="14" font-family="Segoe UI,Inter,Arial">Rank: <tspan fill="{purple2}" font-weight="700">{esc(p.rank)}</tspan></text>
{''.join(boxes)}<text x="38" y="282" fill="{muted}" opacity=".65" font-size="11" font-family="Segoe UI,Inter,Arial">Updated: {esc(p.updated_at)}</text></svg>'''

def main():
    token=os.getenv('HTB_TOKEN','').strip()
    raw_users=[u.strip() for u in os.getenv('HTB_USERS','1132645').split(',') if u.strip()]
    for raw in raw_users:
        m=re.search(r'/users/(\d+)', raw) or re.search(r'^(\d+)$', raw)
        if not m: print(f'[skip] bad id/url: {raw}', file=sys.stderr); continue
        uid=m.group(1)
        p=fetch_with_token(uid, token) if token else None
        if p is None: p=scrape_public(uid)
        (OUT_DIR/f'{uid}.svg').write_text(render_svg(p), encoding='utf-8')
        (OUT_DIR/f'{uid}.json').write_text(json.dumps(asdict(p), indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'[ok] wrote htb/{uid}.svg')
if __name__ == '__main__': main()
