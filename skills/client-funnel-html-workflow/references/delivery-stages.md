# Delivery stages and rollback points

Use these gates in order. A later stage may start only when the current stage has accepted inputs, reviewable outputs, and recorded evidence. Keep project-specific facts, identifiers, credentials, and customer material in the project workspace and handoff—not in this shared reference.

For every stage, record:

- input artifact paths or source references
- output artifact paths
- acceptance evidence and unresolved items
- the decision to proceed, revise, or stop
- the rollback target if verification fails

Evidence levels are defined in `references/acceptance-matrix.md`.

## Discovery

### Acceptable inputs

- Current project handoff, requested pages, intended audience, and authorized final action
- Authorized interviews, briefs, source folders, existing copy, brand references, and example pages
- Known privacy restrictions, claim owners, delivery deadline, and CMS/publishing boundary

### Acceptable outputs

- Source inventory with counts, formats, owners, and review status
- Page and conversion-scope list
- Fact/claim matrix separating verified facts, client statements, inferences, testimonials, numerical claims, and missing confirmations
- Privacy inventory identifying PII, restricted assets, and material that must not enter public copy
- Open-questions list limited to decisions that materially change claims, identity, transmission, publishing, or scope

### Exit evidence

- Every planned page maps to at least one authorized source and a defined purpose.
- Every intended claim is sourced, labeled as unresolved, or removed.
- Public, CMS, browser-control, form-transmission, and deployment permissions are stated explicitly rather than inferred.

### Rollback point

Return to source inventory when a source is missing, duplicated, private, contradictory, or outside authorization. Do not repair uncertainty by inventing copy or broadening access.

## Copy

### Acceptable inputs

- Accepted Discovery inventory and fact/claim matrix
- Standard page structure from `references/page-structure.md`
- Approved brand voice, offer, CTA destination, and SEO terms when SEO is in scope

### Acceptable outputs

- Reviewable copy for homepage, about/brand story, and free-course or registration page
- Claim-to-source map and a visible `上線前確認` list
- CTA map, heading hierarchy, form labels, image roles, and alt-text intent
- Clearly labeled scenarios wherever identity, testimonial permission, or outcome evidence is incomplete

### Exit evidence

- All factual, numerical, credential, outcome, and testimonial statements remain traceable.
- The three pages have distinct roles and a coherent conversion path.
- Fact checking is complete before `humanizer-zh`; tone editing does not change protected facts, links, conditions, or promises.

### Rollback point

Return to Discovery for missing evidence or changed scope. Stay in Copy for structure, clarity, tone, or CTA problems. Never solve a copy gap by creating a new customer fact.

## Design

### Acceptable inputs

- Accepted copy map and heading/CTA hierarchy
- Authorized brand assets, palette references, example pages, and image inventory
- Accessibility and responsive requirements

### Acceptable outputs

- Named design tokens for color, type, spacing, radius, borders, surfaces, and CTA hierarchy
- Section-by-section layout and responsive behavior
- Image plan separating originals, approved derivatives, and generated assets
- Contrast, focus, crop, and text-density decisions for desktop and mobile

### Exit evidence

- Each visual choice supports a content purpose and does not copy protected wording or distinctive branding from a reference page.
- Text/background and control states have an accessible contrast plan.
- Images have documented provenance, intended crop, privacy treatment, and alt-text role.

### Rollback point

Return to Copy when the design requires a new promise, proof point, or content hierarchy. Stay in Design when tokens, layout, imagery, or responsive behavior fail review.

## HTML

### Acceptable inputs

- Accepted copy, design tokens, layouts, and approved project-bound assets
- Defined preview behavior for navigation, CTAs, menus, and forms

### Acceptable outputs

- Semantic three-page HTML, shared CSS/JS, and relative asset paths
- Keyboard-visible controls, useful labels and alt text, responsive navigation, and clear heading hierarchy
- Preview forms that neither transmit nor store data and are visibly labeled as previews
- Loopback preview plus automated and rendered QA evidence

### Exit evidence

- Every asset path resolves, links and CTA anchors behave as intended, and preview form submission is blocked.
- Desktop and 390px/375px mobile views have no unintended horizontal overflow, broken crops, unusable controls, or console errors.
- Accepted HTML is recorded as the content and visual baseline for any later CMS conversion.

### Rollback point

Return to Design for visual-system or layout failures, Copy for content failures, and Discovery for evidence/privacy failures. Keep failed builds local; do not compensate by publishing an unaccepted preview.

## Elementor

### Acceptable inputs

- Accepted HTML baseline and component mapping
- Current project handoff, confirmed target-site readback, explicit write authorization, and a separately scoped unpublished target
- Available native Elementor schemas and current page/global-state snapshots

### Acceptable outputs

- A separate unpublished draft built primarily with native Container, Heading, Text, Image, Button, and other editable widgets
- Structured readback of page status, hierarchy, widget types, settings, asset references, and page-specific CSS state
- A narrow exception log for any HTML widget that could not be represented natively

### Exit evidence

- Target site and target page are confirmed immediately before writing.
- The original homepage, published pages, and global settings remain unchanged unless separately authorized.
- The draft is not a single full-page HTML widget, and readback matches the accepted component map.
- Page CSS/cache regeneration is verified when the target environment requires it.

### Rollback point

If site identity, route, authorization, schema, or readback is uncertain, stop at the accepted HTML baseline. For a separate draft, use the pre-write snapshot to repair it or perform only an explicitly authorized cleanup; never overwrite the original page to make the draft pass.

## QA

### Acceptable inputs

- The accepted stage artifact: local HTML, unpublished Elementor draft, or public URL when publishing is separately in scope
- Acceptance matrix, viewport list, interaction checklist, and approved test-data boundary

### Acceptable outputs

- Evidence ledger covering facts, privacy, accessibility, desktop/mobile rendering, structure, state, links, images, console, and forms
- Desktop and 390px/375px mobile screenshots or equivalent rendered measurements
- Defect list with owner stage, severity, reproduction, and retest result
- Explicit delivery label: local preview, unpublished draft, restricted preview, or verified public page

### Exit evidence

- Required evidence in `references/acceptance-matrix.md` is present for the claimed delivery state.
- Every failed check returns to its owning stage and is rerun after the smallest correction.
- Public availability, production form delivery, analytics, SEO settings, and CMS completion are claimed only when separately in scope and independently verified.

### Rollback point

Route fact/privacy defects to Discovery or Copy, visual/responsive/accessibility defects to Design or implementation, structural defects to Elementor, and delivery-state/form defects to the responsible integration. Preserve the last accepted artifact until the corrected artifact passes fresh QA.
