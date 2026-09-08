# Acceptance matrix

Use the lowest evidence level that directly proves the claim, but do not treat higher numbers as substitutes for different evidence types. For example, a public screenshot does not prove a factual claim, and a structured Elementor readback does not prove mobile rendering.

## Evidence levels

| Level | Meaning | Typical evidence |
|---|---|---|
| L0 | Assertion only; not accepted | Chat statement, memory, unchecked assumption |
| L1 | Authorized source evidence | Supplied brief, approved interview, source document, brand guide, written approval |
| L2 | Artifact or structured readback | Source map, lint/test output, DOM measurement, CMS/API readback, page status, widget tree |
| L3 | Rendered or runtime evidence | Desktop/mobile visual QA, keyboard test, console/network observation, interaction replay |
| L4 | External end-to-end evidence | Public HTTP/content readback, approved form receipt at the intended destination, verified production event |

## Required evidence by area

| Area | Minimum evidence | Acceptance rule | Failure route |
|---|---|---|---|
| Facts and claims | L1 source plus a claim map; L2 readback when copy is stored in an external document or CMS | Every factual, numerical, credential, outcome, and testimonial statement maps to an authorized source. Unconfirmed material is labeled `上線前確認`, converted to a non-identifying scenario, or removed. Rendered text must still match the accepted copy. | Discovery or Copy |
| Privacy | L1 privacy classification; L2 asset/path inspection; L3 rendered inspection | Public-facing artifacts contain no exposed phone numbers, email addresses, addresses, account identifiers, private filenames, readable plates, hidden form data, or unapproved identifiable testimonials. Generated or edited media preserves consent and does not invent identity or outcomes. | Discovery, Copy, or asset preparation |
| Accessibility | L2 markup/static checks plus L3 keyboard and rendered checks | Semantic landmarks and heading order are coherent; controls have labels; informative images have useful alt text; decorative images are ignored appropriately; focus is visible; navigation and forms work by keyboard; text and control contrast are acceptable; reduced viewport or text wrapping does not hide actions. | Design or HTML/Elementor implementation |
| Desktop | L3 rendered evidence at the agreed desktop viewport, default 1280px | Correct page title/H1 and section order; all images load; no unintended horizontal overflow; CTA hierarchy, navigation, spacing, crops, and text density remain usable; console has no relevant errors. | Design or implementation |
| Mobile | L3 rendered evidence at 390px and 375px unless the handoff specifies stricter widths | No unintended horizontal overflow; navigation, controls, forms, headings, images, sticky/fixed elements, and long Traditional Chinese text fit without clipping or overlap. Test both widths after the final change. | Design or implementation |
| Elementor structure | L2 target-site/status/widget-tree/settings readback plus L3 rendered evidence | Target site is confirmed before write; work remains a separate unpublished draft unless publishing is explicitly authorized; native editable widgets form the page hierarchy; a full-page HTML widget is prohibited; exceptions are narrow and logged; page CSS state is refreshed/read back when required. | Elementor |
| Public state | L2 draft/status readback for non-public work; L4 external verification before any public claim | Label the artifact exactly as local preview, unpublished draft, restricted preview, or public page. A public claim requires external HTTP success, expected content/state, required headers or indexing controls, and final URL readback. Localhost, editor preview, CMS status, or a successful deploy command alone is insufficient. | Delivery or deployment |
| Forms | Preview: L2 code/config plus L3 submit/network observation. Production: L4 approved end-to-end receipt | A preview form is visibly non-production, blocks submission, and sends/stores nothing. A production form requires explicit authorization, privacy/consent copy, destination/config readback, an approved non-sensitive test submission, receipt at the intended destination, and duplicate/error behavior checks. Never infer CRM, email, or analytics success from the page UI alone. | HTML/Elementor for preview; form integration for production |

## Delivery-state minimums

| Claimed state | Required evidence |
|---|---|
| Copy accepted | Fact and privacy rows satisfied; unresolved items recorded |
| HTML accepted | Copy accepted plus accessibility, desktop, mobile, assets, links, console, and preview-form checks |
| Elementor draft accepted | HTML baseline accepted plus Elementor L2 structure/status readback and L3 desktop/mobile QA |
| Public page accepted | Relevant prior stage accepted plus public-state L4 verification |
| Production form accepted | Page state accepted plus forms L4 verification |

Record evidence paths, timestamps, viewport sizes, target state, and unresolved exceptions in the project handoff. Re-run affected checks after every corrective edit; stale evidence does not accept a changed artifact.
