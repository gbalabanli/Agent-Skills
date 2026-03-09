# Prompt Patterns

Use these as starting shapes, then tighten them to the user's request.

## Universal Prompt Structure

```text
[subject], [composition], [style], [lighting], [palette], [camera or rendering cues], [constraints], no text
```

## Hero Image

```text
[product or concept] hero image, wide composition, strong focal subject, premium editorial lighting, controlled brand palette, clean background with negative space for layout, high detail, no text
```

## Thumbnail

```text
high-contrast thumbnail for [topic], bold focal subject, simplified background, dramatic lighting, crisp edges, visually legible at small size, no text
```

## Icon

```text
minimal app icon for [product or feature], centered symbol, limited palette, strong silhouette, clean geometry, modern product design language, transparent or simple background
```

## Diagram

```text
clean product diagram of [system or flow], clear separation of components, structured layout, restrained colors, presentation-ready, easy to annotate afterward, no decorative clutter
```

## Pattern or Texture

```text
seamless repeating pattern for [theme], balanced density, controlled motif scale, clean tiling, restrained palette, production-ready texture
```

## Edit Request Pattern

```text
keep the original composition, change only [specific attributes], preserve subject identity, preserve lighting logic, preserve image quality
```

## Restoration Pattern

```text
restore this image, remove damage and artifacts, preserve original subject features, preserve historical character, improve clarity without making it look newly generated
```

## Prompt Tightening Rules

- Name the main subject first.
- Limit the request to one visual goal per generation.
- State exclusions explicitly: `no text`, `no watermark`, `no extra people`, `no busy background`.
- For brand work, specify palette and mood in plain language.
- For revisions, keep the unchanged parts explicit so the model does not drift.
