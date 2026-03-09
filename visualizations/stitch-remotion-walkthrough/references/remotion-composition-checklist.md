# Remotion Composition Checklist

Use this checklist before handing off or rendering a Stitch walkthrough project.

## Setup

- Reuse an existing Remotion project if one already exists.
- Confirm dependencies required by the composition are installed.
- Confirm the screen asset directory exists and uses stable relative paths.
- Confirm the screen manifest exists and matches the current asset set.

## Composition

- Keep slide, composition, and optional overlay logic in separate files.
- Define TypeScript props for reusable components.
- Read screen order, durations, and transition choices from the manifest.
- Keep visual framing consistent across all screens.

## Visual Quality

- Preserve screenshot aspect ratio.
- Keep text overlays readable against the image and background.
- Use motion that emphasizes the UI instead of overwhelming it.
- Verify titles, captions, and callouts appear long enough to read.

## Timing

- Check that each screen duration matches the narrative goal.
- Keep transitions smooth and non-jarring.
- Verify the total video length is reasonable for the requested output.

## Validation

- Preview the composition locally when Remotion is available.
- Smoke-render the final composition when the user asks for a video output.
- Verify the output file path, format, and basic playback before finishing.
- If blocked, leave a runnable project and state the missing dependency or unavailable service.
