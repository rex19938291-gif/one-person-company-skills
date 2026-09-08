# Security Review

Reviewed: 2026-05-30 Asia/Taipei
Source: https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines
Commit reviewed: 180115660cfb8a86b808f117475a01f54caf3bc5
Runtime guideline source reviewed: https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md
Runtime guideline commit reviewed: 4e799d45c17aec1498c269287a83b9dba22b966b

## Decision

Installed.

## Findings

- Skill directory contains only `SKILL.md`.
- No bundled scripts, package-manager hooks, shell command placeholders, credential handling, or destructive commands were found.
- The skill instructs the agent to fetch the latest Vercel Web Interface Guidelines at review time. This is useful for current UI checks but means results can change when the remote guideline changes.
- The runtime guideline file was inspected and contains UI/accessibility review rules, not shell or credential instructions.

## Verification

- GitHub file inventory checked before install.
- Installed `SKILL.md` and runtime guideline file were scanned for shell execution, credential terms, and destructive command indicators.
