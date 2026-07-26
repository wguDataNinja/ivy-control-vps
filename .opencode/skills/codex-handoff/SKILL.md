---
name: codex-handoff
description: Invoke Codex with one composed input prompt file and one Codex-written output file.
license: MIT
compatibility: opencode
---

# Codex Handoff

Use this skill when the user asks to invoke Codex from OpenCode.

## Contract

A Codex handoff has exactly two paths:

1. input file: the complete prompt sent to Codex
2. output file: the artifact Codex is instructed to write

The input file is the primary input to Codex.
The output file path must be included inside the input file before the task instructions.

Do not use CLI output capture.
Do not use fallback commands, runner choices, model choices, or extra intermediate files.

## Input file format

The input file must begin with this handoff header:

```
# Codex Handoff
Your instructions are below.
Write your output to:
```text
<OUTPUT_FILE>

Do not write the final artifact anywhere else.

After writing the output file, respond with a brief completion note.

Instructions

<USER_OR_AGENT_PROMPT>
```

## Preflight

Before invoking Codex:

1. Check that the input file exists.
2. Read the input file.
3. Confirm it begins with the handoff header.
4. Confirm the header contains the intended output file path.
5. Confirm the prompt is appropriate for the user's requested Codex task.

If preflight fails, stop and report the problem. Do not invoke Codex.

Do not edit the input file before running unless the user explicitly asks, except when the user has asked OpenCode to create or prepare the handoff input file.

## Command

Always invoke Codex with this command shape:

```bash
codex exec --skip-git-repo-check -m gpt-5.5 - < "<input-file>"
```

Do not use `--output-last-message`.
Do not redirect stdout to the output file.

Before invoking Codex, print the exact command.

Do not invoke Codex unless the command includes:
- `codex exec`
- `--skip-git-repo-check`
- `-m gpt-5.5`
- `- < "<input-file>"`

## Required behavior

If the user provides input and output paths, use exactly those paths.

If the user provides a raw task prompt rather than a composed input file, create the input file by prepending the handoff header with the selected output path.

If the user asks OpenCode to create the prompt, choose sensible repo-local input and output paths, write the composed input file, then invoke Codex.

Do not treat files referenced inside the prompt as the handoff input. They are only prompt content.

Do not create extra intermediate files unless the user explicitly asks.

## Completion report

After Codex exits, report only:

- command run
- exit code
- output file path
- whether the output file exists
- whether the output file appears to contain the requested artifact
- stderr summary, if any
