# Annotation Tool Usage

## 2-minute quickstart demo

Run one command from repository root:

```bash
python designing/design-to-code-annotator/assets/annotation-tool/scripts/start-demo.py
```

This starts a local HTTP server and opens:

`/designing/design-to-code-annotator/assets/annotation-tool/index.html?demo=1`

The page preloads sample screens + annotations from `references/annotation-export-example.json`.

## Windows start script

Script location (tool home, next to `index.html`):

- `designing/design-to-code-annotator/assets/annotation-tool/start-tool-windows.bat`

From repository root:

```bat
designing\design-to-code-annotator\assets\annotation-tool\start-tool-windows.bat
```

Demo mode:

```bat
designing\design-to-code-annotator\assets\annotation-tool\start-tool-windows.bat --demo
```

Custom port:

```bat
designing\design-to-code-annotator\assets\annotation-tool\start-tool-windows.bat --port 8870
```

## Normal workflow

1. Open `assets/annotation-tool/index.html` in a browser.
2. Upload one or more screen images, or use **Import JSON Project**.
3. Optional: open one or more `.html` designs via **Open HTML designs**.
4. Select a screen from the list.
5. Draw a rectangle over an interactive region.
6. Fill annotation fields and save.
7. Optionally set `Target Screen` to define a transition.
8. Export JSON and markdown.

## Import workflow

- Use **Import JSON Project** to load a previously exported file.
- The tool validates required schema fields and shows readable errors if invalid.
- Imported transitions are rehydrated from `target_screen_id` values.

## Editing behavior

- Click an annotation to edit fields.
- Drag an annotation box to move it.
- Use the bottom-right handle to resize it.
- Overlay coordinates stay aligned on viewport resize because regions are stored in normalized coordinates.
- HTML designs are rendered in an iframe and can be annotated with the same workflow as image screens.
- Annotation mode can be switched between:
  - `Detailed`: full schema fields (interaction type, target screen, component hints, priority, notes).
  - `Easy`: only `Command (Title)` and `Detail`.
- You can switch modes while editing the same annotation.

## HTML design example

- Copied test fixture: `references/examples/html/price-intelligence-mvp-v1.html`

## Keyboard shortcuts

- `Ctrl/Cmd + S`: Save annotation
- `Delete` / `Backspace`: Delete selected annotation
- `Esc`: Clear current selection
- `[` / `]`: Previous/next screen
- `Arrow Up` / `Arrow Down`: Previous/next annotation on current screen

## Validation checklist

- Required annotation fields are populated (`annotation_id`, `label`, region coordinates, interaction metadata).
- `target_screen_id` points to an existing `screen_id` when set.
- Exported markdown includes navigation flow links.
