# fishfactory.dev

Static site for the Fish Factory mobile studio. Plain HTML + CSS + a little vanilla JS, no build step.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Landing page: hero, about, stack, legal, contact |
| `privacy.html` | Privacy Policy for Fish Factory apps |
| `terms.html` | Terms & Conditions (also usable as the custom EULA for the App Store) |
| `delete-account.html` | Account / data deletion instructions (Google Play "Delete account URL") |
| `404.html` | Not-found page served by GitHub Pages |

## WebView mode

Add `?webview=1` to any document URL to hide the site header and footer and follow the system light/dark theme:

```
https://fishfactory.dev/privacy.html?webview=1
https://fishfactory.dev/terms.html?webview=1
https://fishfactory.dev/delete-account.html?webview=1
```

Optional: `&theme=dark` or `&theme=light` forces a theme, for apps that have their own theme switch.
Links between documents keep the parameters.

## Deploy to GitHub Pages

1. Create a repository and push the contents of this folder to the `main` branch.
2. Repository → Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
3. DNS for `fishfactory.dev`:
   - `A` records for the apex → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` record `www` → `<your-github-username>.github.io`
4. Settings → Pages → Custom domain: `fishfactory.dev` (the `CNAME` file already sets it), then enable **Enforce HTTPS** once the certificate is issued.

`requirements/` and `tools/` are not needed by the site. Leave them out of the published repository if you do not want the brief and brandbook to be public.

## Local preview

```
python3 -m http.server 8000
```

Then open <http://localhost:8000>. (The local server does not emulate GitHub's 404 handling; open `/404.html` directly.)

## Brand assets

Every logo image, favicon and the social preview are derived from the supplied logo file by `tools/build_assets.py` (needs Pillow and numpy). Re-run it if the source logo changes:

```
python3 tools/build_assets.py --fonts <folder with SpaceGrotesk.ttf and PlexMono.ttf>
```

Without `--fonts` everything except `assets/img/og-image.png` is regenerated.

## Before publishing the legal documents

The Privacy Policy and Terms are templates. Check these against each real app:

- third-party services named in Privacy Policy §6 (Firebase, RevenueCat are examples)
- retention periods in Privacy Policy §8 and the 30-day deletion window
- governing law and the liability cap in Terms §11 and §15
- the "Last updated" date in each document and `sitemap.xml`
