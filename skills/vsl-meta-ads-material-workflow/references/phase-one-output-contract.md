# Phase One Output Contract

Use this contract whenever `$vsl-meta-ads-material-workflow` is producing你的 Phase One VSL-to-Meta-ads deliverable.

## Phase Boundary

Phase One includes:

- VSL/script analysis
- audience and intent analysis
- TOF/MOF/BOF strategy
- 24 creative angles
- first-pass image prompts, with optional preview images
- de-AI Chinese ad copy
- image prompts
- Google Doc creation
- readback verification

Phase One excludes:

- Meta Ads API connection
- Meta Business Manager authentication
- ad account setup
- campaign/ad set/ad draft creation
- automated upload to Ads Manager
- publishing

Any Meta API or Ads Manager action belongs to Phase Two.

## Google Doc Structure

Create one outline-friendly Google Doc with this structure:

1. H1: Document title
2. Normal metadata line: source script, target product, version date, output phase
3. H1: 文件導覽與漏斗策略總表
4. Table: funnel stage navigation
5. H1: 一、VSL 與產品定位摘要
6. H2: 轉換目標
7. H2: 核心價值主張
8. H2: 受眾與痛點
9. H1: 二、完整廣告漏斗
10. H2: TOF 陌生開發 / 領免費課
11. H2: MOF 免費課後再教育 / 信任建立
12. H2: BOF 成交 / 行動推進
13. H1: 三、24 個素材切角需求
14. H2: TOF 素材
15. H2: MOF 素材
16. H2: BOF 素材
17. H1: 四、首批視覺素材與 Prompt
18. H2 for each generated material
19. H1: 五、素材準備與投放備註
20. H1: 六、Phase Two 延後項目

Use real heading styles, not plain bold text.

## Front Navigation Table

The first table must include:

| 欄位 | 要求 |
| --- | --- |
| 漏斗階段 | TOF / MOF / BOF |
| 核心任務 | This stage's job |
| 主要受眾 | Audience and intent |
| 素材重點名稱 | Angle IDs such as T01-T08 |
| 內文撰寫要素與 CTA | Copy ingredients and action |

Use visual hierarchy with font size, weight, and restrained color. Avoid uniform body-only formatting.

## Creative Angle Table

Each of the 24 angles must include:

| 欄位 | 說明 |
| --- | --- |
| 編號 | T01-T08, M01-M08, B01-B08 |
| 漏斗 | TOF, MOF, BOF |
| 素材名稱 | Short production-friendly title |
| 目標受眾 | Audience segment |
| 受眾意圖 / 痛點 | Internal intent or friction |
| 投放受眾註解 | Cold audience or retargeting window |
| 文案切角 | What the copy should communicate |
| 圖片上文案 | Text intended to appear on image |
| 圖片 Prompt | Full AI image prompt |
| CTA | Button or action direction |

## Retargeting Notes

Use these windows when the source has a lead magnet, free course, free webinar, or similar opt-in:

- Cold/Broad: no prior opt-in; goal is to claim free course or lead magnet.
- 0-7 days after opt-in: high-intent BOF or urgent MOF.
- 8-30 days after opt-in: MOF education and BOF light urgency.
- 31-90 days after opt-in: MOF trust rebuilding and value demonstration.
- 91-180 days after opt-in: TOF/MOF reactivation.
- 181-365 days after opt-in: dream/wish/identity reactivation.
- 366-730 days after opt-in: old-list warming; avoid hard sell first.

Always note whether to exclude purchasers.

## First-Pass Visual Selection

Select 8 visual candidates using this mix unless the VSL dictates otherwise:

- 3 TOF: cold audience or lead-magnet entry angles
- 3 MOF: trust, objection, process, or proof angles
- 2 BOF: offer, urgency, identity, or final-action angles

Prioritize:

- strongest visual scenes
- highest audience-intent diversity
- angles你can judge quickly
- angles likely to become reusable templates

Default output is prompt-first. Generate images only when你explicitly asks, or when the run already has approved generated previews to place into the Google Doc. If images are included, label them as preview references that users can regenerate or adjust.

## Image Prompt Contract

Every generated image prompt must include:

- Asian person, Asian family, or Asian work/lifestyle scene as the main subject
- product/service context from the VSL
- visual style tied to the source page or brand colors
- realistic ad composition with space for image-on-ad text
- no real platform logos unless你explicitly approves
- no watermark
- no unreadable UI details
- no brand marks copied from third parties

Default prompt shape:

```text
Create a Meta ad image for [creative angle].
Main subject: [Asian person/family/work scene].
Scene: [specific situation].
Emotion: [specific feeling].
Visual style: [brand color/style from source].
Composition: leave clear space for the overlay text "[image-on-ad text]".
Avoid: real platform logos, watermarks, payment logos, tiny unreadable text, distorted hands, unrealistic UI.
```

## Copy Contract

For each first-pass generated material, produce:

- Primary text
- Headline
- Description
- CTA
- Image-on-ad text

Apply `humanizer-zh`:

- remove generic AI phrases
- avoid inflated claims
- avoid "不只是...而是..." patterns
- avoid forced three-part lists when two points are enough
- use concrete scenes and direct claims
- preserve truthful uncertainty when needed
- sound like a real marketer writing for actual placement, not a strategy report

## Google Doc Acceptance

Before handoff, verify:

- target Google Doc identity
- H1/H2/H3 headings exist
- front navigation table exists
- 24 creative angles exist
- 8 first-pass visual materials exist
- generated preview images are inserted or clearly linked when available
- prompts and ad copy are visible
- Phase Two deferral is explicit

If images cannot be inserted into the Google Doc through the available connector path, create the Google Doc with image placeholders and include local/generated image paths. State that limitation plainly. If你decides not to generate more images, do not attempt further image generation; use existing approved previews or prompt-only sections.

## GPTs Future Extraction

When你later asks to turn this workflow into a student GPTs tool, extract:

- source-intake prompt
- VSL analysis prompt
- funnel strategy prompt
- 24-angle generation prompt
- copy humanization prompt
- image prompt generation prompt
- Google Doc formatting prompt or output template

Do not build the student GPTs version during Phase One unless你explicitly asks.
