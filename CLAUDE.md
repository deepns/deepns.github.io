# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
bundle install

# Serve locally with live reload (http://localhost:4000/)
bundle exec jekyll serve

# Build for production (output: _site/)
bundle exec jekyll build
```

Changes to `_config.yml` require restarting the Jekyll server. There are no test or lint commands.

## Architecture

This is a Jekyll 3.9.3 personal blog hosted on GitHub Pages with a custom domain (`www.deepanseeralan.com`). Deployment is automatic — pushing to `master` triggers a GitHub Pages build.

**Theme**: [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) loaded as a remote theme (no local theme files). The skin is `air`. The only local theme customization is `_includes/head/custom.html` (favicons).

**Permalink structure**: `/:categories/:title/` — category is part of the URL, so changing a post's category changes its URL.

**Post defaults** are set globally in `_config.yml` (layout, author profile, comments, share, read time, date) so front matter only needs to override exceptions.

## Content Conventions

### Post front matter

```yaml
---
title: Post Title
categories:
    - Tech          # One of: Tech, Books, Learning, Random
tags:
    - tag1
    - tag2
toc: true           # optional: adds table of contents
header:
    teaser: /assets/images/teasers/image.jpg   # optional
    image: /assets/images/headers/image.jpg    # optional full header
    caption: "Caption text"                    # optional
---
```

Post files go in `_posts/` with filename `YYYY-MM-DD-slug.md`.

### Static pages

Pages go in `_pages/` with `layout: single` (or `layout: archive` for archive pages). Archive pages for categories, tags, and year are auto-generated via Liquid layouts — no manual maintenance needed.

### Assets

Post-specific images live under `assets/images/for-posts/<post-slug>/`. Header and teaser images have their own subdirectories under `assets/images/`.

## Key Configuration

All significant site settings (author info, analytics, comments, pagination, plugins) are in `_config.yml`. Comments use Utterances (GitHub issues). Search uses Algolia (`jekyll-algolia` gem). Analytics is GA4.

The `_data/navigation.yml` file controls the top navigation menu.
