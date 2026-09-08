# Elementor Native Blueprint Template

Use this template when producing a continuation packet, implementation plan, or handoff for an HTML/OD to Elementor conversion.

## 1. Scope

- Source:
- Target:
- Current status:
- Non-scope:
- Must confirm first:

## 2. Source Pack

| Item | Path/URL | Purpose | Notes |
| --- | --- | --- | --- |
| Entry HTML/OD artifact | | | |
| CSS/source style | | | |
| JS/interaction source | | | |
| Assets | | | |
| Existing Elementor JSON | | | |
| Preview/evidence | | | |

## 3. Design Tokens

| Token type | Elementor/global target | Value/source |
| --- | --- | --- |
| Colors | Global Colors | |
| Typography | Global Fonts | |
| Max widths | Container settings | |
| Spacing scale | Container padding/gaps | |
| Radius/shadow | Widget/container style | |
| Breakpoints | Responsive settings/CSS | |
| Motion | Native motion or exception | |

## 4. Section Inventory

| Order | Section | Source selector/component | Elementor target | Notes |
| --- | --- | --- | --- | --- |
| 1 | | | Container + widgets | |

For each section, include:

- Purpose:
- Copy:
- Assets:
- Desktop layout:
- Mobile layout:
- Interaction:
- Reusable pattern:

## 5. Widget Tree

Use this shape for each section:

```text
Section: <name>
Container: <outer settings>
 Container: <inner layout settings>
 Heading: "<copy>" / H2 / style token
 Text Editor: "<copy>" / style token
 Image: <asset path or URL> / alt / sizing
 Button: "<label>" / URL / style token
```

For card grids:

```text
Section: <name>
Container: cards-grid flex row wrap
 Card pattern: native Container
 Image/Icon
 Heading
 Text Editor
 Button/link if needed
 Duplication plan:
 Card 1:
 Card 2:
 Card 3:
```

## 6. Asset Map

| Asset | Source | Elementor usage | Needed action |
| --- | --- | --- | --- |
| | | Image widget/background | Upload/copy/reference |

## 7. Exception Register

Every exception must be explicit.

| Exception | Why native widget is not enough | Scope | Editable fallback |
| --- | --- | --- | --- |
| Style-only HTML widget | Elementor controls cannot express this style | Scoped selector only | Copy/content remains native |
| Animation/custom JS | Native motion cannot match source behavior | One section only | Text/media remain native |

Forbidden unless 你 reverses the rule:

- Full-page HTML widget.
- Full-section HTML widget for ordinary text/cards/images/buttons.
- Hard-coded nav links that should come from WordPress menus.

## 8. Verification Plan

- Widget tree has no full-page HTML widget:
- HTML widget exceptions checked:
- Header/footer policy checked:
- Copy parity checked:
- Asset parity checked:
- Desktop viewport checked:
- Mobile viewport checked:
- Horizontal overflow checked:
- Export/package checked:
- Remaining deltas:

## 9. Iteration Capsule

Use this section to make future skill updates easy.

- Reusable rule learned:
- Failure mode:
- Prevention/check:
- Should update skill now:
- Should stay project-only:
- Proposed patch target:
