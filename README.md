# 🇩🇪 German A1 — Study Site

## Project Structure

```
german_a1/
├── index.qmd                  ← Landing page (renders → index.html)
├── _quarto.yml                ← Quarto project config
├── build.sh                   ← ONE command to build everything
│
├── shared/
│   ├── _styles.css            ← All shared CSS (used by every page)
│   └── _app.js                ← Shared JS (sub-dropdown, number converter)
│
└── pages/                     ← One .qmd per topic
    ├── communication.qmd
    ├── countries.qmd
    ├── personal.qmd
    ├── numbers.qmd
    ├── alphabet.qmd
    ├── colors.qmd
    ├── grammar.qmd
    ├── family.qmd
    ├── school.qmd
    ├── time.qmd
    ├── komposita.qmd
    └── hobbies.qmd
```

## Build

```bash
# Render all pages to _site/
./build.sh

# Or with live-reload preview
./build.sh --serve
```

Output is written to `_site/`. Open `_site/index.html` in any browser.

## Adding a New Topic

1. Create `pages/newtopic.qmd` following the same pattern as any existing page
2. Add a card in `index.qmd`
3. Add the nav tab to each existing `pages/*.qmd` navbar block
4. Add subheadings entry in `shared/_app.js`
5. Run `./build.sh`
