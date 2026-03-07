const state = {
  project: {
    project_id: "project-ui-flow",
    project_title: "UI Flow Annotation",
    feature_summary: "",
    screens: [],
    links: []
  },
  currentScreenId: null,
  editingAnnotationId: null,
  drawing: null,
  draftRectNorm: null
};

const ui = {
  projectId: document.getElementById("projectId"),
  projectTitle: document.getElementById("projectTitle"),
  featureSummary: document.getElementById("featureSummary"),
  uploadScreens: document.getElementById("uploadScreens"),
  screenList: document.getElementById("screenList"),
  screenImage: document.getElementById("screenImage"),
  stage: document.getElementById("stage"),
  overlayLayer: document.getElementById("overlayLayer"),
  draftRect: document.getElementById("draftRect"),
  emptyState: document.getElementById("emptyState"),
  annotationForm: document.getElementById("annotationForm"),
  annotationId: document.getElementById("annotationId"),
  label: document.getElementById("label"),
  description: document.getElementById("description"),
  interactionType: document.getElementById("interactionType"),
  expectedResult: document.getElementById("expectedResult"),
  targetScreenId: document.getElementById("targetScreenId"),
  componentHint: document.getElementById("componentHint"),
  developmentNotes: document.getElementById("developmentNotes"),
  priority: document.getElementById("priority"),
  deleteBtn: document.getElementById("deleteBtn"),
  clearBtn: document.getElementById("clearBtn"),
  exportJsonBtn: document.getElementById("exportJsonBtn"),
  exportMdBtn: document.getElementById("exportMdBtn")
};

function genId(prefix) {
  return `${prefix}_${Math.random().toString(36).slice(2, 8)}`;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function currentScreen() {
  return state.project.screens.find((s) => s.screen_id === state.currentScreenId) || null;
}

function updateProjectMeta() {
  state.project.project_id = ui.projectId.value.trim() || "project-ui-flow";
  state.project.project_title = ui.projectTitle.value.trim() || "UI Flow Annotation";
  state.project.feature_summary = ui.featureSummary.value.trim();
}

function updateTargetSelect() {
  const previous = ui.targetScreenId.value;
  ui.targetScreenId.innerHTML = "<option value=\"\">None</option>";
  state.project.screens.forEach((screen) => {
    const opt = document.createElement("option");
    opt.value = screen.screen_id;
    opt.textContent = `${screen.screen_title} (${screen.screen_id})`;
    ui.targetScreenId.appendChild(opt);
  });
  ui.targetScreenId.value = previous;
}

function renderScreenList() {
  ui.screenList.innerHTML = "";
  state.project.screens.forEach((screen) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `screen-item${screen.screen_id === state.currentScreenId ? " active" : ""}`;
    item.textContent = `${screen.screen_title} (${screen.annotations.length})`;
    item.addEventListener("click", () => selectScreen(screen.screen_id));
    ui.screenList.appendChild(item);
  });
  updateTargetSelect();
}

function selectScreen(screenId) {
  state.currentScreenId = screenId;
  state.editingAnnotationId = null;
  clearForm();

  const screen = currentScreen();
  if (!screen) {
    ui.emptyState.classList.remove("hidden");
    ui.screenImage.removeAttribute("src");
    ui.overlayLayer.innerHTML = "";
    return;
  }

  ui.emptyState.classList.add("hidden");
  ui.screenImage.src = screen.image_path;
  renderScreenList();
  renderOverlays();
}

function toNorm(clientX, clientY) {
  const rect = ui.screenImage.getBoundingClientRect();
  const x = clamp((clientX - rect.left) / rect.width, 0, 1);
  const y = clamp((clientY - rect.top) / rect.height, 0, 1);
  return { x, y, rect };
}

function startDrawing(event) {
  if (!currentScreen() || event.target.classList.contains("annotation-box")) {
    return;
  }

  const { x, y } = toNorm(event.clientX, event.clientY);
  state.drawing = { startX: x, startY: y };
  state.draftRectNorm = { x, y, width: 0, height: 0 };
  updateDraftRect();
  ui.draftRect.classList.remove("hidden");
}

function moveDrawing(event) {
  if (!state.drawing) {
    return;
  }
  const { x, y } = toNorm(event.clientX, event.clientY);
  const startX = state.drawing.startX;
  const startY = state.drawing.startY;
  const left = Math.min(startX, x);
  const top = Math.min(startY, y);
  const width = Math.abs(startX - x);
  const height = Math.abs(startY - y);
  state.draftRectNorm = { x: left, y: top, width, height };
  updateDraftRect();
}

function stopDrawing() {
  if (!state.drawing) {
    return;
  }
  const rect = state.draftRectNorm;
  state.drawing = null;
  ui.draftRect.classList.add("hidden");

  if (!rect || rect.width < 0.01 || rect.height < 0.01) {
    return;
  }

  state.editingAnnotationId = null;
  ui.annotationId.value = "";
  ui.label.value = "";
  ui.description.value = "";
  ui.expectedResult.value = "";
  ui.componentHint.value = "";
  ui.developmentNotes.value = "";
  ui.priority.value = "medium";
  ui.interactionType.value = "click";
  ui.targetScreenId.value = "";
  ui.deleteBtn.disabled = true;

  state.draftRectNorm = rect;
}

function updateDraftRect() {
  if (!state.draftRectNorm) {
    return;
  }
  const imgRect = ui.screenImage.getBoundingClientRect();
  const stageRect = ui.stage.getBoundingClientRect();
  const nx = state.draftRectNorm.x;
  const ny = state.draftRectNorm.y;
  const nw = state.draftRectNorm.width;
  const nh = state.draftRectNorm.height;

  ui.draftRect.style.left = `${imgRect.left - stageRect.left + nx * imgRect.width}px`;
  ui.draftRect.style.top = `${imgRect.top - stageRect.top + ny * imgRect.height}px`;
  ui.draftRect.style.width = `${nw * imgRect.width}px`;
  ui.draftRect.style.height = `${nh * imgRect.height}px`;
}

function renderOverlays() {
  const screen = currentScreen();
  ui.overlayLayer.innerHTML = "";
  if (!screen || !ui.screenImage.src) {
    return;
  }

  const imgRect = ui.screenImage.getBoundingClientRect();
  const stageRect = ui.stage.getBoundingClientRect();

  screen.annotations.forEach((ann) => {
    const box = document.createElement("button");
    box.type = "button";
    box.className = `annotation-box${ann.annotation_id === state.editingAnnotationId ? " active" : ""}`;
    box.style.left = `${imgRect.left - stageRect.left + ann.x * imgRect.width}px`;
    box.style.top = `${imgRect.top - stageRect.top + ann.y * imgRect.height}px`;
    box.style.width = `${ann.width * imgRect.width}px`;
    box.style.height = `${ann.height * imgRect.height}px`;
    box.textContent = ann.label;
    box.addEventListener("click", (event) => {
      event.stopPropagation();
      loadAnnotation(ann.annotation_id);
    });
    ui.overlayLayer.appendChild(box);
  });
}

function loadAnnotation(annotationId) {
  const screen = currentScreen();
  const ann = screen?.annotations.find((a) => a.annotation_id === annotationId);
  if (!ann) {
    return;
  }

  state.editingAnnotationId = annotationId;
  state.draftRectNorm = {
    x: ann.x,
    y: ann.y,
    width: ann.width,
    height: ann.height
  };

  ui.annotationId.value = ann.annotation_id;
  ui.label.value = ann.label;
  ui.description.value = ann.description;
  ui.interactionType.value = ann.interaction_type;
  ui.expectedResult.value = ann.expected_result;
  ui.targetScreenId.value = ann.target_screen_id || "";
  ui.componentHint.value = ann.component_hint;
  ui.developmentNotes.value = ann.development_notes;
  ui.priority.value = ann.priority;
  ui.deleteBtn.disabled = false;
  renderOverlays();
}

function clearForm() {
  state.editingAnnotationId = null;
  state.draftRectNorm = null;
  ui.annotationId.value = "";
  ui.annotationForm.reset();
  ui.interactionType.value = "click";
  ui.priority.value = "medium";
  ui.targetScreenId.value = "";
  ui.deleteBtn.disabled = true;
  ui.draftRect.classList.add("hidden");
  renderOverlays();
}

function handleUpload(event) {
  const files = Array.from(event.target.files || []);
  files.forEach((file) => {
    const screenId = genId("screen");
    state.project.screens.push({
      screen_id: screenId,
      screen_title: file.name.replace(/\.[^.]+$/, ""),
      image_path: URL.createObjectURL(file),
      screen_notes: "",
      annotations: []
    });
  });

  renderScreenList();
  if (!state.currentScreenId && state.project.screens.length) {
    selectScreen(state.project.screens[0].screen_id);
  }
}

function saveAnnotation(event) {
  event.preventDefault();
  const screen = currentScreen();
  if (!screen || !state.draftRectNorm) {
    alert("Draw a region on the screenshot before saving.");
    return;
  }

  const annotation = {
    annotation_id: state.editingAnnotationId || genId("ann"),
    label: ui.label.value.trim(),
    x: +state.draftRectNorm.x.toFixed(4),
    y: +state.draftRectNorm.y.toFixed(4),
    width: +state.draftRectNorm.width.toFixed(4),
    height: +state.draftRectNorm.height.toFixed(4),
    interaction_type: ui.interactionType.value,
    description: ui.description.value.trim(),
    expected_result: ui.expectedResult.value.trim(),
    target_screen_id: ui.targetScreenId.value || null,
    component_hint: ui.componentHint.value.trim(),
    development_notes: ui.developmentNotes.value.trim(),
    priority: ui.priority.value
  };

  const idx = screen.annotations.findIndex((a) => a.annotation_id === annotation.annotation_id);
  if (idx >= 0) {
    screen.annotations[idx] = annotation;
  } else {
    screen.annotations.push(annotation);
  }

  state.editingAnnotationId = annotation.annotation_id;
  ui.annotationId.value = annotation.annotation_id;
  ui.deleteBtn.disabled = false;
  renderScreenList();
  renderOverlays();
}

function deleteAnnotation() {
  const screen = currentScreen();
  if (!screen || !state.editingAnnotationId) {
    return;
  }
  screen.annotations = screen.annotations.filter((a) => a.annotation_id !== state.editingAnnotationId);
  clearForm();
  renderScreenList();
}

function buildExportModel() {
  updateProjectMeta();

  const project = {
    project_id: state.project.project_id,
    project_title: state.project.project_title,
    feature_summary: state.project.feature_summary,
    screens: state.project.screens.map((screen) => ({
      screen_id: screen.screen_id,
      screen_title: screen.screen_title,
      image_path: screen.image_path,
      screen_notes: screen.screen_notes || "",
      annotations: screen.annotations.map((ann) => ({ ...ann }))
    })),
    links: []
  };

  project.screens.forEach((screen) => {
    screen.annotations.forEach((ann) => {
      if (ann.target_screen_id) {
        project.links.push({
          link_id: `${screen.screen_id}_${ann.annotation_id}_to_${ann.target_screen_id}`,
          from_screen_id: screen.screen_id,
          from_annotation_id: ann.annotation_id,
          to_screen_id: ann.target_screen_id,
          transition_note: ann.expected_result
        });
      }
    });
  });

  return project;
}

function download(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function toMarkdown(project) {
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
    lines.push(`- **Image**: \`${screen.image_path}\``);
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

    screen.annotations.forEach((ann, idx) => {
      lines.push(`${idx + 1}. **${ann.annotation_id}** (\`${ann.interaction_type}\`)`);
      lines.push(`- Label: ${ann.label}`);
      lines.push(`- Region: x=${ann.x}, y=${ann.y}, w=${ann.width}, h=${ann.height}`);
      lines.push(`- Description: ${ann.description}`);
      lines.push(`- Expected Result: ${ann.expected_result}`);
      lines.push(`- Target Screen: ${ann.target_screen_id || "none"}`);
      lines.push(`- Component Hint: \`${ann.component_hint}\``);
      lines.push(`- Development Notes: ${ann.development_notes}`);
      lines.push(`- Priority: ${ann.priority}`);
    });
    lines.push("");
  });

  lines.push("## 4. Navigation Flow");
  if (project.links.length) {
    project.links.forEach((link, idx) => {
      lines.push(`${idx + 1}. \`${link.from_screen_id}.${link.from_annotation_id}\` -> \`${link.to_screen_id}\``);
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

ui.projectId.addEventListener("input", updateProjectMeta);
ui.projectTitle.addEventListener("input", updateProjectMeta);
ui.featureSummary.addEventListener("input", updateProjectMeta);
ui.uploadScreens.addEventListener("change", handleUpload);
ui.annotationForm.addEventListener("submit", saveAnnotation);
ui.deleteBtn.addEventListener("click", deleteAnnotation);
ui.clearBtn.addEventListener("click", clearForm);
ui.exportJsonBtn.addEventListener("click", () => {
  const project = buildExportModel();
  download(`${project.project_id}.json`, JSON.stringify(project, null, 2), "application/json");
});
ui.exportMdBtn.addEventListener("click", () => {
  const project = buildExportModel();
  download(`${project.project_id}.md`, toMarkdown(project), "text/markdown");
});

ui.stage.addEventListener("mousedown", startDrawing);
window.addEventListener("mousemove", moveDrawing);
window.addEventListener("mouseup", stopDrawing);
window.addEventListener("resize", () => {
  updateDraftRect();
  renderOverlays();
});
ui.screenImage.addEventListener("load", () => {
  renderOverlays();
});

updateProjectMeta();
