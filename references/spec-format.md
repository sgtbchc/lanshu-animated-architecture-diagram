# Animated Excalidraw GIF Spec Format

Use this reference when creating or editing a spec for `scripts/render_animated_diagram.py`.

## Layout Model

The renderer is optimized for a premium dark hand-drawn architecture/process diagram:

1. Top title: `title.prefix` plus highlighted `title.highlight`
2. Top input box: four compact input sources
3. Middle core: three major process cards, a decision diamond, and an output card
4. Bottom left panel: source/context cards
5. Bottom center panel: internal storage or processing layers
6. Bottom right panel: final package/output cards
7. Top right brand slot: dotted mark plus `signature`

Keep the copy short. The renderer uses fixed art-directed positions and applies
basic text fitting in compact regions, but short labels still produce the best
visual hierarchy.

## Recommended Copy Length

- `title.prefix`: 2 to 4 words
- `title.highlight`: 1 to 3 words
- Input labels: 1 word
- Core card title: 1 to 2 words
- Core card body: 2 lines, each under 22 characters
- Panel card title: 1 to 3 words
- Panel card body: 1 to 2 short lines
- Signature: short handle, such as `@岚叔`

## Text Fitting

The renderer automatically fits text in compact labels and cards by wrapping
lines and reducing font size. When a label is still too tight, it may use a
smaller emergency size to preserve the full text. This is intended as a safety
net for labels, not as a replacement for concise copy.

Text fitting is applied to:

- Input labels
- Core card titles and bodies
- Decision diamond text
- Bottom panel cards
- Output and package labels

Manual line breaks in the spec are preserved. English text wraps on spaces,
while CJK text can wrap between characters when needed.

## Animation Timing

Prefer target-duration specs:

```json
"canvas": {
  "width": 1210,
  "height": 1138,
  "duration_seconds": 4,
  "fps": "auto"
}
```

Rules:

- `duration_seconds` is the target GIF length.
- `fps: "auto"` chooses a GIF-safe FPS and derives `frames`.
- Explicit `fps` must be GIF-safe, such as `10`, `20`, `25`, or `50`.
- Avoid `24`, `30`, and `60` FPS for GIF output; GIF frame delays are stored in
  centiseconds, so those values cannot be represented exactly.
- Legacy `frames` plus GIF-safe `fps` still works. The duration is `frames / fps`.

If both `duration_seconds` and `frames` are present, they must agree after the
renderer derives `round(duration_seconds * fps)`.

## Icons

Supported icon keys:

- `folder`
- `file`
- `scan`
- `shield`
- `db`
- `hash`
- `package`

Use simple icons unless the user explicitly provides audited assets. Avoid remote icon libraries by default.

## Quality Bar

The output should include:

- `.png` static preview
- `.gif` animated version
- `.excalidraw` editable source

Verify:

- GIF dimensions match the requested canvas
- GIF has the resolved frame count, FPS, and duration
- Frame-diff shows real motion
- Excalidraw JSON has unique IDs
- All text elements use `fontFamily: 5`
- `files` is empty unless the user explicitly wants embedded images

## Common Command

```bash
python scripts/render_animated_diagram.py \
  --spec assets/default-spec.json \
  --outdir /tmp/diagram-output \
  --basename memory-pack \
  --verify
```
