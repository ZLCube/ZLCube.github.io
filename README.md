# HTB README Card for GitHub Pages

Inserción:

```md
<p align="center">
  <a href="https://app.hackthebox.com/public/users/1132645">
    <img width="70%" src="https://zlcube.github.io/htb/1132645.svg" />
  </a>
</p>
```

Cambia el ID en `.github/workflows/update-htb-card.yml`:

```yaml
env:
  HTB_USERS: "1132645"
```

Para datos más confiables, crea un secret de GitHub Actions llamado `HTB_TOKEN` con tu token de HTB.
