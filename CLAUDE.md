# Repository guide

## Purpose and change posture

This is Gary Wei's hand-built Hugo personal site. It started from Colorlib's Unfold HTML template, but its Hugo templates, data model, image pipeline, and content are maintained directly in this repository; there is no `themes/` directory.

Keep changes narrow and evidence-driven:

- Preserve the dark visual identity and the Colorlib attribution in `layouts/partials/footer/site-footer.html` unless Gary explicitly asks to revisit them.
- Treat biography, employment, education, contact details, analytics choices, legal text, and outbound profiles as owner-controlled public content. Never invent or silently “refresh” them.
- Prefer the existing Hugo/data flow over copying rendered HTML into templates.
- Treat frontend modernization as an explicit migration. CDN, Bootstrap, GSAP, or jQuery changes require end-to-end compatibility and visual checks.
- Keep generated output and unrelated cleanup out of focused changes.

## Toolchain

- Hugo Modules require **Hugo Extended 0.165.0 or newer**; CI pins **Hugo Extended 0.165.0**. Use the CI version for release parity.
- `go.mod` declares Go 1.22.4 and pins Hugo module versions.
- Node is development-only. `package.json` contains Prettier and `prettier-plugin-go-template`; there is no JS bundler and no npm script layer.
- Browser dependencies are CDN assets pinned in `layouts/partials/head/styles.html` and `layouts/partials/footer/scripts.html`.

Install and inspect dependencies with:

```sh
npm ci --include=dev
hugo mod graph
```

`--include=dev` keeps the formatting tools available when the shell has `NODE_ENV=production` or npm is configured to omit development dependencies.

### Hugo module guardrail

**Do not run ordinary `go mod tidy`.** Go cannot see imports declared in Hugo's TOML configuration and will remove the Hugo modules from `go.mod`/`go.sum`. Use Hugo module commands (`hugo mod graph`, `hugo mod get`, `hugo mod clean`) and validate with `go mod verify` plus a real Hugo build.

## Rendering architecture

`layouts/_default/baseof.html` is the global HTML shell. It loads metadata, styles, analytics, the hard-coded navigation, the page's `main` block, the footer, and finally scripts.

### Home page

The home page is assembled through this chain:

1. `content/_index.md` owns page metadata, About prose, page-local assets, and `[params].sections`.
2. `layouts/index.html` iterates `sections` in order and dynamically calls `layouts/partials/body/<section>.html`.
3. Each home partial receives `ctx` (the home page) and `data` (`hugo.Data.index`).
4. `data/index.yaml` supplies the cover, résumé, logos, project cards, education, experience, volunteering, skills, awards, and blogs.

A section name must have a matching body partial. When adding, removing, or reordering a section, trace all coupled sites:

- `content/_index.md` section order and page parameters;
- `layouts/partials/body/<section>.html`;
- the relevant `data/index.yaml` keys;
- the partial's section `id` and any item IDs;
- hard-coded anchors in `layouts/partials/header/site-nav.html`;
- classes/IDs consumed by `assets/js/main.js` and `assets/css/style.css`.

`blogs` and `awards` have retained data and templates but are currently disabled in `content/_index.md`. They are not ready to enable blindly: the blog template ignores `blogs[].img`, and most award images are absent from live asset mounts.

The `data/index.yaml` keys consumed by templates are contracts:

| Key | Shape and coupling |
| --- | --- |
| `background`, `slogan`, `resume` | Cover/about scalars; `background` is a global Hugo asset path. |
| `logos` | `name`, `img`, `link`; links target education/experience/volunteer IDs. |
| `projects` | `class`, `link`, `title`, `note`, `img`; optional `resource` selects a project page bundle for image lookup. `class` also drives Isotope filters and may include Bootstrap grid classes. |
| `blogs` | `class`, `link`, `title`, `note1`, `note2`, `img`; currently dormant. |
| `education` | `id`, `img`, `name`, `title`, optional Markdown `note`. |
| `experience`, `volunteer` | `name`, `title`, `time`, Markdown `note`, usually `id`, and either `img` or `svg`. |
| `awards` | `img`, `title`, `date`, `content`; `content` is retained legacy metadata and is not rendered. |
| `skills` | `svg`, `title`, Markdown `note`. |

### Content pages

- Ordinary pages such as `content/impressum.md` use `layouts/_default/single.html`.
- `/projects/` uses `layouts/_default/section.html`; taxonomy pages use `layouts/_default/taxonomy.html`.
- `content/projects/<slug>/index.md` files are leaf bundles with type `projects`.
- The default project template is `layouts/projects/single.html`; `layout = "plain"` selects `layouts/projects/plain.html`.
- The full project template consumes `params.background`, `subtitle`, `url`, `authors`, and `images`. SEO also depends on `description`, `keywords`, and `og_image`.
- `params.url` is only the rendered “Visit” link; it is not Hugo's top-level URL override.
- `archetypes/default.md` creates only title/date/draft and does not satisfy the project-template contract.
- Project Markdown intentionally mixes raw HTML and shortcodes. Goldmark has block attributes and `unsafe = true`; the local `color`, `deeppink`, and `pfl-col` shortcodes render their inner Markdown.
- External Markdown links pass through `layouts/_default/_markup/render-link.html`, which applies configured `target` and `rel` values.

## Image and asset rules

There are three live image namespaces. Copy a neighboring pattern rather than guessing a path:

| Use | Storage | Typical reference |
| --- | --- | --- |
| Global processed image | `assets/images/` | `resources.Get "images/foo.jpg"`; responsive partials commonly receive `assets/images/foo.jpg`. |
| Project page resource | `content/projects/<slug>/images/` | `.Resources.Get "images/foo.jpg"` or a responsive partial with the project page as `ctx` and `images/foo.jpg`. |
| Verbatim public file | `static/` | Root-relative URL such as `/images/svg/foo.svg` or `/fonts/icomoon.woff`. |

Additional contracts:

- `og_image` and project backgrounds try the current page bundle first, then global `assets/` resources.
- `picture`, `figure`, and `img` are supplied by `github.com/future-wd/hugo-responsive-images`; `images/image` comes from `github.com/hugomods/images`. They are module dependencies, not missing local files.
- Both image modules ship a Markdown render hook. Import order makes `hugomods/images` the active Markdown-image hook; do not apply the responsive partial's `assets/...` path convention to Markdown images without tracing the active hook.
- Every responsive partial call must receive the correct page `ctx`, especially for page-bundle images.
- `config/_default/params.toml` configures Lanczos resizing, seven widths, WebP, and lazysizes. Production validation must exercise image processing.
- `static/uploads` is also mounted as `assets/uploads` for pipeline access.
- `archived/` is not mounted and is not published. Promote an archived image into a live namespace before referencing it.
- `assets/css/icomoon/style.css` plus `static/fonts/icomoon.*` are one generated/vendored icon set. Regenerate them together rather than hand-editing glyph mappings.

## Frontend runtime and coupling

`assets/js/main.js` is legacy jQuery code adapted from Unfold. It assumes globals loaded in footer order, including Bootstrap/Popper, Owl Carousel, AOS, Isotope, imagesLoaded, GSAP 2, ScrollMagic, jarallax, and related plugins. `assets/css/style.css` contains both active styles and retained template-era selectors.

Important DOM contracts:

- Navigation, mobile-menu cloning, scroll state, GSAP reveal classes, Isotope filters, carousels, loaders, and form states are coupled across templates, `main.js`, and `style.css`. Trace all three before renaming a class or ID.
- Relative project links receive `ajax-load-page`. `main.js` fetches the target and extracts `.portfolio-single-wrap`; internal project layouts must keep that wrapper or opt out of AJAX deliberately.
- The home page appends `assets/js/contact-form.js` through `[params].js`. It expects both `#contactForm` and the contact section, and it submits to an external Formspree endpoint. Preview tests must not send a real message.
- `[params].css` and `[params].js` append page-specific pipeline assets. Hugo minifies and fingerprints local CSS/JS; `hugo.IsServer`, not the environment name, controls whether SRI attributes are emitted.
- Plugin globals used by `main.js` remain hard runtime dependencies unless each initialization is removed or guarded. Remove a CDN dependency only after tracing all calls.
- The full-page loader has dependency-independent native load/timeout fallback and a no-JavaScript CSS fallback in `baseof.html`; preserve both when changing script loading.
- CDN upgrades require compatible URLs, integrity hashes, load order, data attributes, and regression checks. Updating only a URL is incomplete.

## Known sharp edges

Do not fix these incidentally, but do not mistake them for intended guarantees:

- `layouts/projects/single.html` uses a literal `"Jan 2nd, 2006"`, so most rendered ordinal suffixes are wrong.
- `layouts/partials/head/p/schema.html` is the active itemprop partial. The similarly named `layouts/partials/head/schema.html` is unreferenced legacy code and references incompatible/missing parameter names.
- Development configuration still enables Google Analytics, Cronitor, and Pirsch with placeholder IDs.
- The footer uses `time.Now` when `generate_date_on_footer = true`, so output changes across build dates even when content does not.
- Hard-coded template links with `target="_blank"` do not automatically inherit the Markdown render-hook `rel` policy.

## Style and editing conventions

- Follow `.editorconfig`: UTF-8, LF, two-space indentation, and final newline, except local shortcode templates intentionally omit the final newline.
- Follow `.prettierrc`: single quotes, ES5 trailing commas, 150-column width, and the Go-template parser for HTML.
- Markdown and selected legacy/generated files are intentionally excluded in `.prettierignore`.
- Format only supported files touched by the task. Avoid whole-tree formatting or inherited CSS churn unless cleanup is the task.

Targeted formatting commands:

```sh
npm exec -- prettier --check path/to/file
npm exec -- prettier --write path/to/file
```

## Verification

Run the narrowest relevant checks, then finish every source change with a production build:

```sh
go mod verify
hugo --gc --minify --environment production --panicOnWarning
git diff --check
```

When changing JavaScript, also run:

```sh
node --check assets/js/main.js
node --check assets/js/contact-form.js
```

When changing supported formatted files, run targeted Prettier checks. When changing the workflow, run `actionlint` if available.

For markup, CSS, JavaScript, navigation, or content-layout work, preview locally:

```sh
hugo server --environment development --buildDrafts
```

Inspect the affected route at desktop and mobile widths. When relevant, exercise the fixed/scrolled nav, mobile menu, project filters, internal AJAX project view/back action, carousels, lazy images, and contact validation without submitting the form.

`public/`, `resources/_gen/`, `.hugo_build.lock`, and `node_modules/` are generated/ignored. Do not edit or commit them.

## Deployment boundary

`.github/workflows/deploy_aws.yml` is deployment-sensitive:

- It triggers for pushes to `deploy`, pull requests targeting `deploy`, and manual dispatches.
- Checkout is explicitly pinned to `ref: deploy`; a pull-request run therefore does not validate the PR head as written.
- The production build is synchronized to S3 with `--delete`, then CloudFront is invalidated globally.
- AWS credentials and resource identifiers belong in GitHub Actions secrets; never place them in repository files or logs.
- The workflow lacks concurrency protection, so overlapping deployments deserve explicit review.

Do not push `deploy`, run the workflow, sync S3, invalidate CloudFront, or change deployment credentials unless Gary explicitly requests that side effect. A successful local production build is the default completion boundary.
