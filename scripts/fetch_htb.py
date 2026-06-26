#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

from render_svg import render_svg


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; htb-readme-card/1.0; +https://github.com/ZLCube/ZLCube.github.io)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def normalize_users(raw: str) -> list[str]:
    users = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        match = re.search(r"/public/users/(\d+)", item)
        users.append(match.group(1) if match else item)
    return users


def deep_find_user(payload: Any, user_id: str) -> Optional[Dict[str, Any]]:
    candidates: list[Dict[str, Any]] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            keys = {str(k).lower() for k in obj.keys()}
            values = {str(v) for v in obj.values() if isinstance(v, (str, int))}
            if (
                str(user_id) in values
                and (
                    {"name", "username"} & keys
                    or {"rank", "rank_text"} & keys
                    or "respect" in keys
                )
            ):
                candidates.append(obj)
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)

    walk(payload)
    if not candidates:
        return None

    candidates.sort(key=lambda d: len(d.keys()), reverse=True)
    return candidates[0]


def extract_next_data(html: str, user_id: str) -> Optional[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None

    try:
        payload = json.loads(script.string)
    except json.JSONDecodeError:
        return None

    return deep_find_user(payload, user_id)


def extract_from_text(html: str, user_id: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    data: Dict[str, Any] = {
        "id": user_id,
        "user_id": user_id,
        "username": "HTB User",
        "rank": "Unknown",
    }

    title = soup.find("title")
    if title and title.text:
        clean = title.text.replace("Hack The Box", "").replace("|", "").strip()
        if clean:
            data["username"] = clean.split()[0]

    meta_title = soup.find("meta", attrs={"property": "og:title"})
    if meta_title and meta_title.get("content"):
        content = str(meta_title["content"])
        if content.strip():
            data["username"] = content.split("|")[0].strip()

    patterns = {
        "respect": r"Respect\s*[:\n ]+([0-9,.]+)",
        "points": r"Points\s*[:\n ]+([0-9,.]+)",
        "rank": r"Rank\s*[:\n ]+([A-Za-z0-9 _-]+)",
        "user_owns": r"User Owns\s*[:\n ]+([0-9,.]+)",
        "system_owns": r"System Owns\s*[:\n ]+([0-9,.]+)",
        "challenge_owns": r"Challenge Owns\s*[:\n ]+([0-9,.]+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip()

    return data


def normalize_profile(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    profile = dict(data)
    if "profile" in profile and isinstance(profile["profile"], dict):
        profile.update(profile["profile"])
    if "user" in profile and isinstance(profile["user"], dict):
        profile.update(profile["user"])

    normalized: Dict[str, Any] = {
        "id": str(profile.get("id") or profile.get("user_id") or user_id),
        "user_id": str(user_id),
        "username": (
            profile.get("username")
            or profile.get("name")
            or profile.get("nickname")
            or profile.get("userName")
            or "HTB User"
        ),
        "rank": profile.get("rank") or profile.get("rank_text") or profile.get("rankName") or "Unknown",
        "respect": profile.get("respect") or profile.get("respects"),
        "points": profile.get("points") or profile.get("user_owns_points"),
        "user_owns": profile.get("user_owns") or profile.get("users_owned") or profile.get("userOwns"),
        "system_owns": profile.get("system_owns") or profile.get("systems_owned") or profile.get("systemOwns"),
        "challenge_owns": profile.get("challenge_owns") or profile.get("challenges_owned") or profile.get("challengeOwns"),
        "raw_keys": sorted(str(k) for k in profile.keys()),
        "updated_at": now_utc(),
        "source": f"https://app.hackthebox.com/public/users/{user_id}",
    }

    return normalized


def fetch_profile(user_id: str) -> Dict[str, Any]:
    url = f"https://app.hackthebox.com/public/users/{user_id}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    data = extract_next_data(response.text, user_id)
    if data is None:
        data = extract_from_text(response.text, user_id)

    return normalize_profile(data, user_id)


def write_outputs(profile: Dict[str, Any], out_dir: Path) -> None:
    user_id = str(profile["user_id"])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{user_id}.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / f"{user_id}.svg").write_text(render_svg(profile), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate static HTB profile cards for GitHub Pages.")
    parser.add_argument("--users", default=os.getenv("HTB_USERS", "1132645"), help="Comma-separated HTB IDs or public profile URLs.")
    parser.add_argument("--out", default="htb", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out)
    users = normalize_users(args.users)

    if not users:
        print("No HTB users provided.", file=sys.stderr)
        return 1

    first_svg: Optional[Path] = None
    first_json: Optional[Path] = None

    for user_id in users:
        print(f"[+] Fetching HTB profile {user_id}")
        try:
            profile = fetch_profile(user_id)
        except Exception as exc:
            print(f"[!] Could not fetch {user_id}: {exc}", file=sys.stderr)
            profile = normalize_profile(
                {
                    "id": user_id,
                    "user_id": user_id,
                    "username": f"HTB User {user_id}",
                    "rank": "Unavailable",
                    "respect": "—",
                    "points": "—",
                    "user_owns": "—",
                    "system_owns": "—",
                    "challenge_owns": "—",
                },
                user_id,
            )
            profile["error"] = str(exc)

        write_outputs(profile, out_dir)

        if first_svg is None:
            first_svg = out_dir / f"{user_id}.svg"
            first_json = out_dir / f"{user_id}.json"

    if first_svg and first_json:
        shutil.copyfile(first_svg, out_dir / "latest.svg")
        shutil.copyfile(first_json, out_dir / "latest.json")

    print("[+] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
