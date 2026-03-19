# Design-to-Code Annotator Tool

This folder contains the browser annotation app:

- `index.html`
- `app.js`
- `model.js`
- `styles.css`

## Start on Windows

From repository root:

```bat
designing\design-to-code-annotator\assets\annotation-tool\start-tool-windows.bat
```

Demo mode (preloaded sample project):

```bat
designing\design-to-code-annotator\assets\annotation-tool\start-tool-windows.bat --demo
```

Custom port:

```bat
designing\design-to-code-annotator\assets\annotation-tool\start-tool-windows.bat --port 8870
```

## Start with Python (cross-platform)

Normal mode:

```bash
python -m http.server 8765
```

Then open:

`http://127.0.0.1:8765/designing/design-to-code-annotator/assets/annotation-tool/index.html`

Demo mode:

`http://127.0.0.1:8765/designing/design-to-code-annotator/assets/annotation-tool/index.html?demo=1`
