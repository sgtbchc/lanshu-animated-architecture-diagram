# Bundled Fonts

This skill bundles fonts so PNG/GIF rendering does not depend on macOS, Windows, or Linux system font availability.

## Fonts

- `PatrickHand-Regular.ttf`
  - Source: https://github.com/google/fonts/tree/main/ofl/patrickhand
  - License: SIL Open Font License, see `OFL-PatrickHand.txt`
  - Use: hand-drawn Latin text and titles
- `LXGWWenKai-Regular.ttf`
  - Source: https://github.com/lxgw/LxgwWenKai
  - License: SIL Open Font License, see `OFL-LXGWWenKai.txt`
  - Use: CJK text
- `LXGWWenKai-Medium.ttf`
  - Source: https://github.com/lxgw/LxgwWenKai
  - License: SIL Open Font License, see `OFL-LXGWWenKai.txt`
  - Use: bold CJK text

## Cross-Platform Notes

- Do not rely on `/System/Library/Fonts/...`; those paths are macOS-only.
- Do not rely on `C:\Windows\Fonts\...`; those paths are Windows-only and may vary by edition.
- `ImageFont.load_default()` is only a last fallback. It ignores the intended visual scale and can make 40+ point text render like tiny labels.
- Keep font files in this directory when moving the skill to another machine.
- Always render with `--check`; it validates that the bundled fonts exist and that probe text renders above the readability threshold.
