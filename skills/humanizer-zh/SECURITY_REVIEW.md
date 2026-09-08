# Security Review

Reviewed: 2026-07-12 Asia/Taipei
Sources:

- https://github.com/kevintsai1202/Humanizer-zh-TW
- https://github.com/op7418/Humanizer-zh
- https://github.com/Raymondhou0917/speak-human-tw

The `speak-human-tw` repository, root `SKILL.md`, linked references, localization rules, human-voice rules, benchmark, evaluation instructions, and MIT license were inspected read-only on 2026-07-11 to 2026-07-12.

## Decision

Updated as a local hardened and modular copy. It keeps the Codex trigger name `humanizer-zh`, preserves你的 `social-post-codex` routing, and selectively adopts `speak-human-tw` methods for protected content, scene intensity, long-form fidelity, human-voice boundaries, and SF/SNF regression testing. The upstream package was not installed or executed.

## Findings

- The reviewed upstream is documentation-driven; no upstream script was installed or executed.
- No package-manager hooks, background network calls, credential handling, or destructive commands were copied into the local skill.
- Both relevant upstream sources use the MIT license; the local license retains attribution for incorporated sources.
- Upstream `SKILL.md` frontmatter grants `Read`, `Write`, `Edit`, and `AskUserQuestion`; the installed copy removes that tool grant so file edits remain governed by the normal session permission flow.
- No `npx`, package install, clone, or upstream code execution was used for this update. Markdown was inspected read-only and the useful methods were manually adapted.
-你FB/IG-specific writing rules are intentionally not embedded here; they live in `<你的本機路徑>`.

## Verification

- GitHub file inventory and linked source files were checked before update.
- Upstream `SKILL.md`, pattern, localization, humanization, benchmark, evaluation, and license files were compared at a rules level.
- Installed `SKILL.md` was scanned for source markers, Traditional Chinese rules, shell execution, network commands, credential terms, and destructive command indicators.
- Follow-up scan confirmed你-specific social-post rules were removed from this generic skill and isolated under `social-post-codex`.
- Ruby YAML checks passed for `SKILL.md` and `agents/openai.yaml`; all seven Markdown links resolve; 38 patterns and 20 minimum regression cases are present.
