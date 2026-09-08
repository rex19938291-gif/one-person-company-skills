---
name: vsl-meta-ads-material-workflow
description: "Turn a Google Drive VSL, webinar script, sales script, product page, or campaign brief into a Meta ads material workflow for你: TOF/MOF/BOF strategy, 24 creative angles, de-AI Chinese ad copy, image prompts, optional first-pass image previews, placement notes, and an outline-friendly Google Doc. Use when你asks to 調取 VSL 腳本, 產出廣告素材需求, 建立素材流, 建立 Meta 廣告素材包, or prepare Phase One creative validation before Meta Ads API automation."
---

# VSL Meta Ads Material Workflow

Use this skill to convert a VSL or sales script into a Phase One Meta ads creative package for你.

Phase One means: strategy, copy, image prompts, optional generated-image previews, and a Google Doc for你的 review. Do not connect to Meta Ads API, create ad drafts, touch Business Manager, or publish ads in Phase One.

## Required Reference

Before producing the deliverable, read:

- `references/phase-one-output-contract.md`

Use it as the output contract, not as optional guidance.

## Input Sources

Accept any of these as source material:

- Google Drive or Google Docs VSL script
- sales script or webinar script
- activity page or product page
- campaign brief
-你的 spoken notes about audience, pain points, offer, funnel, or retargeting windows

If你names a Google Drive document by title, use the Google Drive connector to find and read the exact document before planning content. If multiple candidates match, ask你to choose.

## Workflow

1. Gather source material.
 - Read the VSL/script and any product or campaign page你provides.
 - Extract conversion goal, offer, free lead magnet, price/value anchor, audience, emotional promise, objections, proof, and CTA.

2. Build the funnel strategy.
 - Define TOF, MOF, and BOF roles.
 - Include cold-audience development for free-course or lead-magnet opt-in.
 - Include retargeting windows when relevant: 0-7, 8-30, 31-90, 91-180, 181-365, and 366-730 days.
 - Keep Phase Two Meta API automation explicitly out of scope.

3. Create 24 creative angles.
 - Default split: TOF 8, MOF 8, BOF 8.
 - Each angle must have audience, intent, copy angle, image-on-ad text, image prompt, CTA, and ad-operations note.
 - Make the angles diverse enough for Meta Andromeda / Advantage+ to route different user intents.

4. Select first-pass visual-preview angles.
 - Choose the highest learning-value mix across TOF/MOF/BOF.
 - Include cold-audience opt-in angles first when the campaign has a free-course or lead magnet.
 - Default to prompt-first output. Generate image previews only when你explicitly asks or when a current test run already has approved images to place into the Google Doc.

5. Write Meta ad copy.
 - Produce primary text, headline, description, CTA, and image-on-ad text.
 - Use `humanizer-zh` principles: direct language, varied rhythm, no inflated AI-style phrasing, no forced three-part structure, no generic hype.
 - Keep the text usable as a first draft in Ads Manager.

6. Prepare image assets.
 - Treat AI images as adjustable previews, not locked final art.
 - Use the built-in image generation path only when你explicitly asks for generation.
 - Every image prompt must specify Asian people or Asian family/work/lifestyle context as the main visual subject.
 - Match the product/page visual style and avoid real platform logos, payment logos, or brand marks unless你provides approval.

7. Build the Google Doc.
 - Use real H1/H2/H3 heading styles.
 - Put a funnel navigation table near the top.
 - Include all 24 angles and any approved preview images available for the run.
 - Include prompts, copy, and ad-operations notes under each generated material.
 - Verify with connector readback. For image-heavy or layout-sensitive documents, also use export/readback checks available in the Google Docs workflow.

8. Report Phase One status.
 - Provide the Google Doc link, generated image count, verification performed, and what is intentionally deferred to Phase Two.
 - Do not mark the workflow complete until你can inspect the document and assets.

## Output Defaults

- Language: Traditional Chinese.
- Document audience: course lecturer, marketer, or你preparing ad production.
- Tone: practical, operator-ready, not academic.
- First-pass image count: prompt-first by default; optional preview images only when requested or already generated for validation.
- Full creative-angle count: 24.
- Primary document format: Google Doc with outline navigation.
- Phase Two deferral: Meta Ads API, ad account connection, campaign/ad set/ad draft creation, and publishing.

## Quality Bar

The output is not finished if it is only a strategy memo. It must be usable for production:

- A lecturer can record from it.
- A designer or user can create from the prompts and adjust visual direction manually.
-你can judge copy and image quality from it.
- A future Phase Two agent can map the material into Meta campaign/ad set/ad draft automation.
