# Scene library

Read at the concept step of every chapter. Propose a set of scenes per chapter from this list, show it to the user, and let them swap, add or drop scenes before building. Every scene below exists as working code in `defaults/scenes/`. Its names, mailboxes, titles and versions come from the scene data (below), its colours and fonts from the theme tokens (`reference/theme.md`). Copy the functions you need into the film's `scenes.js`; copy `defaults/scenes/scenes.json` next to `SERIES.md` and replace its example data.

| Scene | What it shows | Best for | Example code |
|---|---|---|---|
| Title build | logo or glyph, kicker, title types or scrambles in, underline draws | chapter openers | `example-intro-scenes.js` (s1), `explainer-address-path-split.js` (title) |
| Before / after snap | an old phrase sits loose and tilted, snaps into the new one on the beat | "until now… now it's built in" | `example-intro-scenes.js` (s2) |
| Object grows into object | an icon (envelope) grows into a system box with a typed label | introducing a component | `example-intro-scenes.js` (s3) |
| Feature tiles | 3 tiles land on the beat, then join under one bar or lock | listing what you get | `example-intro-scenes.js` (s4) |
| Big reveal | one word on the drop with shake and glitch | product or feature name | `example-intro-scenes.js` (s5) |
| Chapter strip | chips light up as the narrator names them | series overview, agenda | `example-intro-scenes.js` (s6) |
| Identifier card | a long identifier (address, key, URL) types in, tags land on the beat, a prefix springs in | explaining what something is | `explainer-address-path-split.js` |
| Path animation | an object travels from node A through hops to node B along a drawn route | data, mail or request flow | `explainer-address-path-split.js` |
| Split screen | two frozen or playing footage panels side by side with labels and chips | "sent" vs "arrived", before vs after | `explainer-address-path-split.js` |
| Terminal rebuild | a real log replayed in a styled terminal, slowing at key lines with a step card | deploys, CLI work, anything too fast to read | `terminal-rebuild-checklist.js` |
| Recap checklist | items check off one per beat | what one action gave you | `terminal-rebuild-checklist.js` |
| Footage highlights | rings and pills on real UI elements, freeze while each is explained, plates covering what must not show | walkthroughs over recordings | `footage-highlights.js` |
| Flow with switch | two systems side by side, a config switch flips, items flow across, a loop arrow for "repeatable" | migrations, imports, syncs | `migration-flow-endcard.js` |
| Warning card | a "before you start" card with chips | breaking changes, prerequisites | `migration-flow-endcard.js` |
| End card | NEXT card or closing line, logo, music credit, fade to canvas | every chapter end; series end | `terminal-rebuild-checklist.js` (s3), `migration-flow-endcard.js` |
| Title card | "CHAPTER NN" kicker and the chapter title rising word by word (`reveal` preset), logo, for 2.5 s in the series theme | between chapters of the long video only; `film.py join` makes one per chapter from the chapter's `film.css` and `assets.js` and its `voiceover.json` `"title"` | `title-card.js` |

## Scene data

`scenes.json` holds every name, mailbox, title and version the library shows. `film.py` takes the film's own `scenes.json`, else the one next to `SERIES.md`, writes it to `src/scene-data.js` as `window.SCENE_DATA` and adds `<script src="scene-data.js"></script>` before `scenes.js` in the film's `index.html`. The data is part of the page code, so a change re-renders the affected chapter.

| Key | Type | Used for | Example |
|---|---|---|---|
| `product` | string | title and end cards, with `version` | `"Acme"` |
| `version` | string | title and end cards, the "major release" warning | `"2.0"` |
| `domain` | string | addresses typed on screen, DKIM `d=` | `"example.test"` |
| `component` | string | the system a scene reveals or migrates to | `"Acme Mail"` |
| `previous` | string | the system a migration starts from | `"Legacy Mail"` |
| `switch` | string | the config switch flipped in a migration | `"import_legacy"` |
| `terminal` | string | the terminal window title | `"acme · deploy"` |
| `people` | list of `{name, mailbox}` | lower thirds; the first signs in, the second sent the mail | `[{"name": "Maria Example", "mailbox": "maria@example.test"}, ...]` |
| `mailboxes` | list of strings, up to 3 shown | mailbox rows, migrated items, the accounts step | `["alex@example.test", ...]` |
| `chapters` | list of strings, up to 6 shown | the series strip | `["Deploy", "Mail", ...]` |
| `next` | string | the NEXT card | `"09 · Moving from Legacy Mail"` |
| `onion` | `{address, left, right}` | the identifier card and the path nodes | a 56-character example address |
| `credit` | string | the music credit on the end card | `"Music: original, made with ACE-Step 1.5"` |
| `log` | list of strings, optional | the replayed terminal log; without it a placeholder log runs | the lines of a real deploy |

Use invented data only: `example.test` style domains and made-up names. Keep real customer data, credentials and production addresses out of `scenes.json`.

## Motion presets

Build motion from the presets in `../motion-designer/templates/shared/presets.js` (table and calls in `SKILL.md`, section 3): `reveal` for text, `focus` for the camera, `cursor`, `captions`, `spotlight`, `emphasize` for a callout tied to a line, `morph` and `transition("whip")` between states and shots, `parallax`, `tilt`, `chart`, `aurora`, `motionBlur`, `rackFocus`. Time them with `line(id)` and `scene(id)` so they follow the voice, for example `emphasize(t, "n05", rect, "TLS included")` or `reveal(words, t, line("n01").start)`.

## Picking scenes

- One scene per idea; a chapter of 60-90 s usually has 3-5 scenes plus an end card.
- Explain, then show: a short motion scene that explains the idea, then the footage that proves it, then a recap.
- Put the biggest reveal on a musical drop (`music_edit.py` prints where drops land).
- Footage scenes keep the real UI legible: plates over empty space, never over what is being explained.
