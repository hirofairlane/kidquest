# Credits & Attribution

The KidQuest **source code** is MIT-licensed (see [LICENSE](LICENSE)). This file tracks
third-party assets and content with their own licenses.

## Graphical assets

_None bundled yet._ When art is added (hand-made, third-party packs, or AI-generated), list
it here with its source and license, and keep a compliance checklist.

| Asset / pack | Source | License | Notes |
|---|---|---|---|
| — | — | — | — |

## AI-generated content

Sprites and illustrations may be generated locally with ComfyUI using a **curated allowlist**
of safe pixel-art LoRAs. Generated game content (levels, dialogues) is produced by a local LLM.

Content-safety policy: KidQuest is for children. Image generation is restricted to an explicit
allowlist of family-safe models; any NSFW model is banned. Generated text passes a safety/scope
filter and a manual review gate before publishing.

## Test fixtures

`fh2m/tests/fixtures/*.fh2m` are **unmodified sample maps from the fheroes2 project**
([ihhub/fheroes2](https://github.com/ihhub/fheroes2), GPL-2.0), used only as
read-only test data to verify the `.fh2m` container round-trip. They are not part
of the shipped product. (R7 cleanup may switch these to fetch-on-demand.)

## Fonts

_To be added (a high-legibility schoolbook font for the youngest profile)._ Record the font
name and license here when bundled.
