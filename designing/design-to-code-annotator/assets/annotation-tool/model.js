const REQUIRED_ANNOTATION_FIELDS = [
  "annotation_id",
  "label",
  "x",
  "y",
  "width",
  "height",
  "interaction_type",
  "description",
  "expected_result",
  "target_screen_id",
  "component_hint",
  "development_notes",
  "priority"
];

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function isNormNumber(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1;
}

function isNullableString(value) {
  return value === null || typeof value === "string";
}

function toPosixPath(path) {
  return path.replaceAll("\\", "/");
}

function joinPath(basePath, filePath) {
  if (!basePath) {
    return filePath;
  }
  const normalizedBase = toPosixPath(basePath).replace(/\/+$/, "");
  const normalizedFile = toPosixPath(filePath).replace(/^\/+/, "");
  return `${normalizedBase}/${normalizedFile}`;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function withResolvedPath(pathValue, basePath) {
  if (!isNonEmptyString(pathValue)) {
    return pathValue;
  }
  if (pathValue.startsWith("blob:") || pathValue.startsWith("data:")) {
    return pathValue;
  }
  if (/^https?:\/\//i.test(pathValue)) {
    return pathValue;
  }
  return basePath ? joinPath(basePath, pathValue) : pathValue;
}

function normalizeAnnotation(annotation) {
  return {
    annotation_id: String(annotation.annotation_id),
    label: String(annotation.label),
    x: +clamp(annotation.x, 0, 1).toFixed(4),
    y: +clamp(annotation.y, 0, 1).toFixed(4),
    width: +clamp(annotation.width, 0, 1).toFixed(4),
    height: +clamp(annotation.height, 0, 1).toFixed(4),
    interaction_type: String(annotation.interaction_type),
    description: String(annotation.description),
    expected_result: String(annotation.expected_result),
    target_screen_id: annotation.target_screen_id === null ? null : String(annotation.target_screen_id),
    component_hint: String(annotation.component_hint),
    development_notes: String(annotation.development_notes),
    priority: String(annotation.priority)
  };
}

export function validateImportProject(rawProject) {
  const errors = [];
  if (!isObject(rawProject)) {
    return {
      valid: false,
      errors: ["Project must be a JSON object."]
    };
  }

  if (!isNonEmptyString(rawProject.project_id)) {
    errors.push("Missing or invalid `project_id`.");
  }
  if (!isNonEmptyString(rawProject.project_title)) {
    errors.push("Missing or invalid `project_title`.");
  }
  if (!Array.isArray(rawProject.screens)) {
    errors.push("Missing or invalid `screens` array.");
  }

  const screenIds = new Set();
  const transitions = [];

  if (Array.isArray(rawProject.screens)) {
    rawProject.screens.forEach((screen, screenIndex) => {
      const at = `screens[${screenIndex}]`;
      if (!isObject(screen)) {
        errors.push(`${at} must be an object.`);
        return;
      }

      if (!isNonEmptyString(screen.screen_id)) {
        errors.push(`${at}.screen_id is required.`);
      } else {
        if (screenIds.has(screen.screen_id)) {
          errors.push(`${at}.screen_id must be unique.`);
        }
        screenIds.add(screen.screen_id);
      }
      if (!isNonEmptyString(screen.screen_title)) {
        errors.push(`${at}.screen_title is required.`);
      }
      const rawRenderType = screen.render_type;
      if (rawRenderType !== undefined && !["image", "html"].includes(rawRenderType)) {
        errors.push(`${at}.render_type must be image or html.`);
      }
      const renderType = rawRenderType === "html" ? "html" : "image";
      const sourcePath = screen.design_path ?? screen.image_path;
      if (!isNonEmptyString(sourcePath)) {
        errors.push(`${at}.design_path or image_path is required.`);
      }
      if (!Array.isArray(screen.annotations)) {
        errors.push(`${at}.annotations must be an array.`);
        return;
      }

      screen.annotations.forEach((annotation, annotationIndex) => {
        const annAt = `${at}.annotations[${annotationIndex}]`;
        if (!isObject(annotation)) {
          errors.push(`${annAt} must be an object.`);
          return;
        }

        REQUIRED_ANNOTATION_FIELDS.forEach((fieldName) => {
          if (!(fieldName in annotation)) {
            errors.push(`${annAt}.${fieldName} is required.`);
          }
        });

        if (!isNonEmptyString(annotation.annotation_id)) {
          errors.push(`${annAt}.annotation_id must be a non-empty string.`);
        }
        if (!isNonEmptyString(annotation.label)) {
          errors.push(`${annAt}.label must be a non-empty string.`);
        }
        if (!isNormNumber(annotation.x)) {
          errors.push(`${annAt}.x must be between 0 and 1.`);
        }
        if (!isNormNumber(annotation.y)) {
          errors.push(`${annAt}.y must be between 0 and 1.`);
        }
        if (!isNormNumber(annotation.width) || annotation.width <= 0) {
          errors.push(`${annAt}.width must be > 0 and <= 1.`);
        }
        if (!isNormNumber(annotation.height) || annotation.height <= 0) {
          errors.push(`${annAt}.height must be > 0 and <= 1.`);
        }
        if (!isNonEmptyString(annotation.interaction_type)) {
          errors.push(`${annAt}.interaction_type must be a non-empty string.`);
        }
        if (!isNonEmptyString(annotation.description)) {
          errors.push(`${annAt}.description must be a non-empty string.`);
        }
        if (!isNonEmptyString(annotation.expected_result)) {
          errors.push(`${annAt}.expected_result must be a non-empty string.`);
        }
        if (!isNullableString(annotation.target_screen_id)) {
          errors.push(`${annAt}.target_screen_id must be a string or null.`);
        }
        if (!isNonEmptyString(annotation.component_hint)) {
          errors.push(`${annAt}.component_hint must be a non-empty string.`);
        }
        if (!isNonEmptyString(annotation.development_notes)) {
          errors.push(`${annAt}.development_notes must be a non-empty string.`);
        }
        if (!["high", "medium", "low"].includes(annotation.priority)) {
          errors.push(`${annAt}.priority must be high, medium, or low.`);
        }
        if (typeof annotation.target_screen_id === "string" && annotation.target_screen_id.trim()) {
          transitions.push({
            at: annAt,
            target: annotation.target_screen_id
          });
        }
      });
    });
  }

  transitions.forEach((transition) => {
    if (!screenIds.has(transition.target)) {
      errors.push(`${transition.at}.target_screen_id points to unknown screen "${transition.target}".`);
    }
  });

  return {
    valid: errors.length === 0,
    errors
  };
}

export function normalizeImportedProject(rawProject, options = {}) {
  const imageBasePath = options.imageBasePath || "";
  const normalizedScreens = (rawProject.screens || []).map((screen) => ({
    render_type: screen.render_type === "html" ? "html" : "image",
    screen_id: String(screen.screen_id),
    screen_title: String(screen.screen_title),
    design_path: withResolvedPath(String(screen.design_path || screen.image_path), imageBasePath),
    image_path: withResolvedPath(String(screen.image_path || screen.design_path), imageBasePath),
    screen_notes: typeof screen.screen_notes === "string" ? screen.screen_notes : "",
    annotations: (screen.annotations || []).map((annotation) => normalizeAnnotation(annotation))
  }));

  return buildExportModelFromProject({
    project_id: String(rawProject.project_id),
    project_title: String(rawProject.project_title),
    feature_summary: typeof rawProject.feature_summary === "string" ? rawProject.feature_summary : "",
    screens: normalizedScreens,
    links: []
  });
}

export function buildExportModelFromProject(project) {
  const out = {
    project_id: project.project_id,
    project_title: project.project_title,
    feature_summary: project.feature_summary || "",
    screens: (project.screens || []).map((screen) => ({
      render_type: screen.render_type === "html" ? "html" : "image",
      screen_id: screen.screen_id,
      screen_title: screen.screen_title,
      design_path: screen.design_path || screen.image_path,
      image_path: screen.image_path,
      screen_notes: screen.screen_notes || "",
      annotations: (screen.annotations || []).map((annotation) => ({ ...annotation }))
    })),
    links: []
  };

  out.screens.forEach((screen) => {
    screen.annotations.forEach((annotation) => {
      if (annotation.target_screen_id) {
        out.links.push({
          link_id: `${screen.screen_id}_${annotation.annotation_id}_to_${annotation.target_screen_id}`,
          from_screen_id: screen.screen_id,
          from_annotation_id: annotation.annotation_id,
          to_screen_id: annotation.target_screen_id,
          transition_note: annotation.expected_result
        });
      }
    });
  });

  return out;
}

export function toMarkdown(project) {
  const lines = [];
  lines.push(`# Build Brief: ${project.project_title}`);
  lines.push("");
  lines.push("## 1. Overview");
  lines.push(`- **Project ID**: ${project.project_id}`);
  lines.push(`- **Feature Summary**: ${project.feature_summary || "unknown"}`);
  lines.push("");
  lines.push("## 2. Screen Inventory");

  project.screens.forEach((screen) => {
    lines.push(`### ${screen.screen_id} - ${screen.screen_title}`);
    lines.push(`- **Render Type**: \`${screen.render_type === "html" ? "html" : "image"}\``);
    lines.push(`- **Design Source**: \`${screen.design_path || screen.image_path}\``);
    lines.push(`- **Screen Notes**: ${screen.screen_notes || "none"}`);
    lines.push(`- **Annotation Count**: ${screen.annotations.length}`);
    lines.push("");
  });

  lines.push("## 3. Interactive Elements");
  project.screens.forEach((screen) => {
    lines.push(`### ${screen.screen_id}`);
    if (!screen.annotations.length) {
      lines.push("- No annotations.");
      lines.push("");
      return;
    }

    screen.annotations.forEach((annotation, index) => {
      lines.push(`${index + 1}. **${annotation.annotation_id}** (\`${annotation.interaction_type}\`)`);
      lines.push(`- Label: ${annotation.label}`);
      lines.push(`- Region: x=${annotation.x}, y=${annotation.y}, w=${annotation.width}, h=${annotation.height}`);
      lines.push(`- Description: ${annotation.description}`);
      lines.push(`- Expected Result: ${annotation.expected_result}`);
      lines.push(`- Target Screen: ${annotation.target_screen_id || "none"}`);
      lines.push(`- Component Hint: \`${annotation.component_hint}\``);
      lines.push(`- Development Notes: ${annotation.development_notes}`);
      lines.push(`- Priority: ${annotation.priority}`);
    });
    lines.push("");
  });

  lines.push("## 4. Navigation Flow");
  if (project.links.length) {
    project.links.forEach((link, index) => {
      lines.push(`${index + 1}. \`${link.from_screen_id}.${link.from_annotation_id}\` -> \`${link.to_screen_id}\``);
      lines.push(`- Transition note: ${link.transition_note}`);
    });
  } else {
    lines.push("- No explicit screen transitions.");
  }

  lines.push("");
  lines.push("## 5. Implementation Notes");
  lines.push("- Reusable components:");
  lines.push("- State and validation constraints:");
  lines.push("- API and data dependencies:");
  lines.push("");
  lines.push("## 6. Open Questions");
  lines.push("- Any missing copy, states, or API contracts?");

  return lines.join("\n");
}
