# HTB README Card for GitHub Pages

Generate a Hack The Box profile card as a static SVG using GitHub Actions + GitHub Pages.

## Insert in Markdown / GitHub README

Replace only the HTB user ID:

```md
<p align="center">
  <a href="https://app.hackthebox.com/public/users/1132645">
    <img width="70%" src="https://ZLCube.github.io/htb/1132645.svg" />
  </a>
</p>
```

For other users:

```md
<p align="center">
  <a href="https://app.hackthebox.com/public/users/HTB_USER_ID">
    <img width="70%" src="https://YOUR_GITHUB_USERNAME.github.io/htb/HTB_USER_ID.svg" />
  </a>
</p>
```

## Configure your HTB ID

Edit `.github/workflows/update-htb-card.yml`:

```yaml
env:
  HTB_USERS: "1132645"
```

Multiple cards:

```yaml
env:
  HTB_USERS: "1132645,123456,987654"
```

## Run manually

```bash
pip install -r requirements.txt
python scripts/fetch_htb.py --users 1132645 --out htb
```

## Notes

- GitHub Pages cannot run backend scraping per request.
- The SVG is static and refreshed by GitHub Actions.
- If HTB changes its public profile page structure, update `scripts/fetch_htb.py`.
- For README `<img>`, query-string routing like `?user=1132645` is not reliable for static generation. This project uses `/htb/<id>.svg` instead.
