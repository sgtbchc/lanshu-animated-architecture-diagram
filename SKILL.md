---
name: lanshu-animated-architecture-diagram
description: Create premium hand-drawn architecture and process diagrams in the Lanshu animated GIF style, with editable .excalidraw files, static PNG previews, and genuinely animated GIFs with moving flow highlights. Use this skill whenever the user asks for 岚叔动态架构图, Excalidraw-like diagrams, DailyDoseOfDS-style black-background sketches, animated architecture/process GIFs, polished flowcharts, visual explanations of articles or system designs, or asks to replicate or improve a reference diagram with hand-drawn animated effects.
---

# Lanshu Animated Architecture Diagram

Create a polished black-background hand-drawn technical diagram with:

- Editable `.excalidraw` source
- Static `.png` preview
- Animated `.gif` with moving glow points and pulsing module highlights

Use the bundled renderer for deterministic output. Avoid external icon libraries unless the user explicitly provides audited assets.

## Workflow

1. Extract the diagram content.
   - For an article or long post, identify the core architecture, actors, stages, data flow, decisions, and final outputs.
   - For a reference image, preserve the visual grammar: title structure, panels, arrows, density, and signature placement.

2. Create a spec JSON.
   - Start from `assets/default-spec.json`.
   - Keep labels short. Read `references/spec-format.md` when field details or copy length guidance are needed.
   - Use the user’s language for explanatory labels unless the reference style clearly calls for English titles.
   - Prefer `canvas.duration_seconds` plus `canvas.fps: "auto"` for GIF timing. Use explicit GIF-safe FPS values such as `10`, `20`, `25`, or `50` only when the user asks for a specific cadence.

3. Render the outputs.

```bash
python /path/to/skill/scripts/render_animated_diagram.py \
  --spec /path/to/spec.json \
  --outdir /path/to/output-dir \
  --basename descriptive-name \
  --verify \
  --check
```

4. Validate before delivery.
   - Use `--check` to confirm PNG/GIF dimensions, FPS, frame count, animation motion, bundled font availability, ffprobe media metadata, and Excalidraw output contracts.
   - Treat GIF timing as resolved output: if `duration_seconds` is set, the renderer computes frame count; `--check` verifies the actual GIF metadata against the resolved timing.
   - Use `--verify` output to prove the GIF is not static.
   - Use `scripts/check_portability.py` when moving or reinstalling the skill to confirm all required assets, Python dependencies, and independent media inspection tools are present.
   - Treat `ffprobe` as the independent media verifier for GIF metadata. Avoid relying on the renderer's own Pillow checks as the only evidence chain.
   - Confirm bundled font assets are present and readable; `--check` validates this with probe text so Windows does not silently fall back to tiny PIL default fonts.
   - Confirm `.excalidraw` JSON has unique IDs, text uses `fontFamily: 5`, and `files` is empty. `--check` validates these output contracts automatically.
   - Open the PNG preview visually and fix overlap, cramped text, or weak hierarchy.

5. Deliver the three files.
   - Show the GIF preview when the interface supports local images.
   - Link the PNG and `.excalidraw` source.

## Style Rules

- Use a dark canvas with a thin outer rounded frame.
- Use one highlighted title phrase in a green capsule.
- Put the author signature in the top-right brand slot unless the user asks otherwise.
- Prefer clean white main arrows. Use colored motion only in the GIF overlay.
- Keep static diagrams restrained. Let animation add motion, not clutter.
- Use short text. If a phrase cannot fit, rewrite it instead of shrinking until unreadable.
- Use built-in simple icons: `folder`, `file`, `scan`, `shield`, `db`, `hash`, `package`.

## Spec Authoring Hints

Animation timing is configurable. To request a four-second GIF, use:

```json
"canvas": {
  "width": 1210,
  "height": 1138,
  "duration_seconds": 4,
  "fps": "auto"
}
```

Use `fps: "auto"` unless the user needs a specific cadence. GIF frame delays are stored in centiseconds, so values such as `30` FPS and `60` FPS are not reliable for exact metadata; the renderer rejects unsafe values early. Legacy specs with explicit `frames` plus GIF-safe `fps` still work.

Map common content to the fixed layout:

- `inputs`: source systems, triggers, documents, tools, or user actions
- `core.cards`: the three main stages of the process
- `decision`: the quality gate or readiness check
- `left_panel`: memory/context/source material
- `center_panel`: internal layers, safeguards, archive stores, or pipeline internals
- `right_panel`: packaged outputs, reusable assets, generated reports, or agent-facing artifacts

If the subject has more than three stages, group adjacent steps into three core cards and move details into the lower panels.

## Verification Commands

Use these checks after rendering. `--check` combines renderer-side checks with an independent `ffprobe` media metadata check:

```bash
python /path/to/skill/scripts/check_portability.py /path/to/skill
```

```bash
python /path/to/skill/scripts/render_animated_diagram.py \
  --spec spec.json \
  --outdir outputs \
  --basename diagram \
  --verify \
  --check
```

You can also run `ffprobe` directly to inspect a GIF by hand:

```bash
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames \
  -show_entries format=duration \
  -of default=noprint_wrappers=1 output.gif
```

The `--verify` report should show nonzero changed pixels between sampled GIF frames.
The `--check` report should return `"ok": true`; it exits nonzero on contract failures.
