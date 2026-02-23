# Copilot Instructions for deepns.github.io

This is a Jekyll-based personal blog hosted on GitHub Pages.

## Build and Serve

```bash
# Install dependencies
bundle install

# Serve locally (watches for changes)
bundle exec jekyll serve

# Build for production
bundle exec jekyll build
```

The site is built into the `_site/` directory. Local development server runs on `http://localhost:4000/`.

## Key Technologies

- **Jekyll 3.9.3**: Static site generator
- **Theme**: Minimal Mistakes (remote theme via mmistakes/minimal-mistakes)
- **Markdown processor**: kramdown
- **Ruby**: Dependency management via Bundler

## Important Gems

- `jekyll-paginate`: Pagination for posts
- `jekyll-sitemap`: Auto-generates sitemap
- `jekyll-feed`: RSS/Atom feeds
- `jekyll-gist`: Embed GitHub gists
- `jekyll-algolia`: Search indexing
- `utterances`: Comments system
- `jemoji`: Emoji support
- `jekyll-include-cache`: Performance optimization for includes

## Directory Structure

- `_posts/`: Blog posts (filename format: `YYYY-MM-DD-slug.md`)
- `_pages/`: Static pages (about, 404, archives)
- `_includes/`: Reusable template components (e.g., `_includes/head/`)
- `_data/`: Data files for the site
- `_plugins/`: Custom Jekyll plugins
- `assets/`: CSS, JavaScript, images
- `_config.yml`: Main Jekyll configuration

## Content Conventions

### Post Format

All posts use YAML front matter and follow this pattern:

```markdown
---
title: Post Title
toc: true  # optional: table of contents
categories:
    - Category Name
tags:
    - tag1
    - tag2
---

Post content in markdown...
```

Key defaults (set in `_config.yml`):
- Layout: `single`
- Author profile enabled
- Reading time shown
- Comments enabled (via Utterances)
- Share buttons enabled

### Pages

Static pages in `_pages/` follow the same front matter format but use `layout: single` and have no categories/tags. Archive pages use `layout: archive` with specific variables.

## Site Configuration

Key settings in `_config.yml`:

- **Timezone**: America/New_York
- **Paginate**: 5 posts per page
- **Permalink**: `/:categories/:title/`
- **Author links**: Twitter, GitHub, LinkedIn
- **Analytics**: Google Analytics (GA4)
- **Comments**: Utterances (GitHub issues-based)
- **Category/Tag archives**: Auto-generated via liquid layouts

## Build Notes

- Changes to `_config.yml` require restarting the Jekyll server
- The theme is pulled from GitHub as a remote theme (no local theme directory)
- Google site verification and Analytics tracking IDs are configured
- Search is enabled (Algolia plugin available)

## Common Tasks

**Add a new post**: Create `_posts/YYYY-MM-DD-slug.md` with proper front matter and markdown content.

**Create a static page**: Add to `_pages/` directory with appropriate layout.

**Update site metadata**: Edit author info, social links, or analytics in `_config.yml` (requires server restart).

**Preview locally**: Run `bundle exec jekyll serve` and check `http://localhost:4000/`.
