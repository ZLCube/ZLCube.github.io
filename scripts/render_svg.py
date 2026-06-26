from __future__ import annotations

from html import escape
from typing import Any, Dict


def _value(data: Dict[str, Any], *keys: str, default: str = "—") -> str:
    for key in keys:
        value = data.get(key)
        if value is not None and str(value).strip() != "":
            return str(value)
    return default


def render_svg(data: Dict[str, Any]) -> str:
    username = escape(_value(data, "username", "name", default="HTB User"))
    user_id = escape(_value(data, "id", "user_id", default="unknown"))
    rank = escape(_value(data, "rank", "rank_text", default="Unknown"))
    respect = escape(_value(data, "respect", "respects", default="—"))
    points = escape(_value(data, "points", "user_owns_points", default="—"))
    system_owns = escape(_value(data, "system_owns", "systems_owned", "owned_machines", default="—"))
    user_owns = escape(_value(data, "user_owns", "users_owned", default="—"))
    challenges = escape(_value(data, "challenge_owns", "challenges_owned", "owned_challenges", default="—"))
    updated_at = escape(_value(data, "updated_at", default="—"))

    profile_url = escape(f"https://app.hackthebox.com/public/users/{user_id}")

    return f"""<svg width="780" height="270" viewBox="0 0 780 270" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Hack The Box stats for {username}</title>
  <desc id="desc">Static HTB profile card generated with GitHub Actions.</desc>

  <defs>
    <linearGradient id="border" x1="0" y1="0" x2="780" y2="270" gradientUnits="userSpaceOnUse">
      <stop stop-color="#9FEF00"/>
      <stop offset="0.45" stop-color="#2E333D"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.35"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0.623 0 0 0 0 0.937 0 0 0 0 0 0 0 0 0.35 0"/>
      <feBlend in="SourceGraphic" mode="screen"/>
    </filter>
  </defs>

  <rect x="1" y="1" width="778" height="268" rx="18" fill="#0D1117" stroke="url(#border)" stroke-width="2"/>
  <circle cx="690" cy="55" r="62" fill="#9FEF00" opacity="0.08" filter="url(#glow)"/>
  <circle cx="705" cy="58" r="28" fill="#9FEF00" opacity="0.16"/>

  <text x="32" y="48" fill="#FFFFFF" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="26" font-weight="700">Hack The Box Stats</text>
  <text x="32" y="80" fill="#8B949E" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="14">{profile_url}</text>

  <text x="32" y="124" fill="#9FEF00" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="30" font-weight="800">{username}</text>
  <text x="32" y="154" fill="#C9D1D9" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="18">Rank: {rank}</text>

  <g font-family="Segoe UI, Ubuntu, Arial, sans-serif">
    <rect x="32" y="180" width="150" height="58" rx="12" fill="#161B22" stroke="#30363D"/>
    <text x="50" y="203" fill="#8B949E" font-size="13">Respect</text>
    <text x="50" y="226" fill="#FFFFFF" font-size="22" font-weight="700">{respect}</text>

    <rect x="200" y="180" width="150" height="58" rx="12" fill="#161B22" stroke="#30363D"/>
    <text x="218" y="203" fill="#8B949E" font-size="13">Points</text>
    <text x="218" y="226" fill="#FFFFFF" font-size="22" font-weight="700">{points}</text>

    <rect x="368" y="180" width="150" height="58" rx="12" fill="#161B22" stroke="#30363D"/>
    <text x="386" y="203" fill="#8B949E" font-size="13">User owns</text>
    <text x="386" y="226" fill="#FFFFFF" font-size="22" font-weight="700">{user_owns}</text>

    <rect x="536" y="180" width="150" height="58" rx="12" fill="#161B22" stroke="#30363D"/>
    <text x="554" y="203" fill="#8B949E" font-size="13">System owns</text>
    <text x="554" y="226" fill="#FFFFFF" font-size="22" font-weight="700">{system_owns}</text>
  </g>

  <text x="32" y="258" fill="#484F58" font-family="Segoe UI, Ubuntu, Arial, sans-serif" font-size="12">Challenges: {challenges} · Updated: {updated_at}</text>
</svg>
"""
