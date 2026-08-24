# Project cover generator

Generates the 1280x720 images used by the home-page project grid. Title, spacing,
colors, and export settings live in `covers.json`; full-bleed art lives in
`backgrounds/`, while diagrams, screenshots, and logos live in `sources/`.

Rasterized covers contain the project title and, only when the image needs
context, one short description. Categories and dates remain in
`data/index.yaml` and appear in the hover overlay. All generated titles use the
same 108px size, and all optional descriptions use the same 64px size, matching
the proportions in the original 2560x1440 Photoshop sources.

Cover gradients use a restrained Genshin-inspired elemental palette built from
`66`, `cc`, and `ff` channel pairs, for example `#66ccff`, `#cc66ff`,
`#ffcc66`, `#ff6666`, and `#66ffcc`. Keep one clear palette per card and use
real project artwork only when it carries information at card size.

## Generate a cover

```sh
uv run scripts/project-covers/generate.py eden
```

Omit the project name to regenerate every configured cover.

The original Photoshop files use **Comic Sans MS Bold** at an effective
1280x720 size of about 108px. The generator therefore prefers that historical
font and uses the bundled OFL-licensed `ComicNeue-Bold.ttf` only as a fallback:

1. `--font /path/to/font.ttf`
2. `PROJECT_COVER_FONT`
3. `/mnt/windows/Windows/Fonts/comicbd.ttf`
4. bundled `ComicNeue-Bold.ttf`

The Windows font is never copied into this repository. Generated JPEGs use
4:4:4 chroma, contain no EXIF metadata, are progressive and optimized, and are
verified at 1280x720 before the command succeeds.

## Add a project

1. Add full-bleed art under `backgrounds/`, or add real project artwork under
   `sources/` and configure its panel in `covers.json`.
2. Add one entry to `covers.json`.
3. Run the generator with that entry's name.
4. Preview the resulting card at desktop and mobile widths.

Use real project art or a deliberately generated background. Do not bake URLs,
dates, or category labels into the image; those remain structured data in
`data/index.yaml`.
