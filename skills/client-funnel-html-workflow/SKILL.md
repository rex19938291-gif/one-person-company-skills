---
name: client-funnel-html-workflow
description: Turn client interviews, Drive source folders, brand references, example funnel pages, and existing draft copy into verified Traditional Chinese homepage, brand-story/about, and free-course landing-page HTML previews. Use when你asks to reproduce the structure of reference pages, improve incomplete website copy, derive a visual system, generate or optimize client imagery, build responsive static HTML, show an in-app Browser preview, or prepare the result for later Elementor conversion.
---

# Client Funnel HTML Workflow

## Overview

Build a reviewable three-page client funnel from source collection through copy, image direction, responsive HTML, and visual QA. Keep claims traceable, protect private customer material, and separate preview completion from production publishing.

## Required workflow

### 1. Establish scope and durable state

- Read the selected project `TASK_HANDOFF.md` in full and treat it as current truth.
- Record the required pages, reference URLs, source folders, output directory, and authorized final action.
- Default deliverables are `index.html`, `about.html`, `free-course.html`, shared CSS/JS, and project-bound assets.
- Do not infer authorization to publish, deploy, submit forms, or modify WordPress.

### 2. Inventory and preprocess sources

- Use `safe-data-preprocess` for mixed Drive folders, Office files, PDFs, screenshots, or large source sets unless a structured Drive/Docs/Sheets API preserves fidelity better.
- Produce a compact source inventory with counts and categories before drafting.
- Separate verified facts, client quotes, numerical claims, inferred themes, and missing confirmations.
- Never expose private filenames, phone numbers, email addresses, license plates, or raw customer identifiers in public copy or handoffs.

### 3. Reverse-engineer reference structure

- Use `browser:control-in-app-browser` for the exact reference pages.
- Extract section order, content purpose, CTA placement, trust-building pattern, image roles, spacing rhythm, and mobile behavior.
- Reuse information architecture, not copyrighted sentences, distinctive branding, or pixel-for-pixel styling.
- For the standard three-page funnel, compare against `references/page-structure.md`.

### 4. Build the evidence-backed copy map

- Home: hero promise, audience problem, brand introduction, free-resource CTA, method/services, values, proof, closing CTA.
- About: personal origin, three story arcs with tension/turn/lesson, relevant experience, belief, CTA.
- Free course: promise, form, three learning outcomes, audience fit, proof, instructor trust, repeated CTA.
- Each claim must map to a source. Mark unresolved numbers, outcomes, credentials, and testimonials as `上線前確認`.
- Use generic scenario copy when photo-to-testimonial identity cannot be verified.
- Run `humanizer-zh` after fact verification and before the final CTA/SEO pass.

### 5. Derive the visual system

- Translate the client’s palette reference into named tokens: ink, primary, secondary, accent, surface, border, and CTA.
- Preserve accessible contrast and do not introduce unrelated high-saturation colors.
- Use `你-web-design-guidelines`, `frontend-design`, and `responsive-web-ui-guard` for implementation decisions.
- Prefer restrained radius, coherent spacing, semantic headings, and one primary CTA hierarchy.

### 6. Prepare and generate imagery

- Inventory original portraits, lifestyle images, logos, vehicles, and testimonial assets before generation.
- View every local source image before editing it.
- Use `imagegen` for composition, background cleanup, lighting, privacy cleanup, aspect-ratio adaptation, and palette alignment.
- Preserve real people’s identity and body proportions. Do not invent customers, outcomes, vehicles, credentials, or testimonial statements.
- Remove readable plates and distracting private/commercial details when appropriate.
- Generate images without embedded copy, logos, or watermarks unless the user explicitly requests them.
- Copy every accepted output into the project asset folder with a versioned filename; retain the original generated file.

### 7. Build responsive HTML

- Use semantic HTML and a shared design-token stylesheet.
- Make navigation, buttons, form labels, alt text, keyboard focus, and mobile menu usable.
- Preview forms must not transmit or store data; clearly label them as non-submitting previews.
- Keep client source assets separate from generated derivatives.
- Use relative asset paths and verify every referenced file exists.
- If Elementor conversion is later requested, invoke `html-to-elementor` only after HTML acceptance.

### 8. Verify and present

- Start a loopback-only local server.
- Validate all three pages at desktop width and at least one mobile breakpoint.
- Check: correct H1, image load success, no horizontal overflow, no console errors, navigation links, CTA anchors, and preview-form behavior.
- Visually compare section rhythm, palette, image crops, and text density against the references.
- Open the accepted pages in the in-app Browser and finalize only user-facing preview tabs as deliverables.
- Report exact local paths, preview URL, verification results, and outstanding `上線前確認` items.

### 9. Close the loop

- Read the latest handoff again before updating it.
- Record sources used, copy status, generated asset paths, HTML paths, verification evidence, unresolved approvals, and the next safe step.
- Do not call the workflow production-ready until public HTTP, form delivery, analytics, and CMS behavior have each been separately verified when in scope.

## Stop gates

Stop and ask你only when a decision changes public claims, identity matching, external data transmission, production writes, deployment, paid generation volume, or use of sensitive/private material outside the provided scope. Continue with clearly labeled placeholders for ordinary non-blocking gaps.

## References

- Read `references/page-structure.md` when planning the standard three-page section map.
- Read `references/delivery-stages.md` before starting or handing off a stage; use its accepted inputs, outputs, exit evidence, and rollback point.
- Read `references/acceptance-matrix.md` when accepting Copy, HTML, Elementor, QA, public-state, or form-delivery claims.
