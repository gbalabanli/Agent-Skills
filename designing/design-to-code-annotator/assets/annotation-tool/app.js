import {
  buildExportModelFromProject,
  normalizeImportedProject,
  toMarkdown,
  validateImportProject
} from "./model.js";

const MIN_RECT_SIZE = 0.01;

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
  draftRectNorm: null,
  interaction: null
};

const ui = {
  projectId: document.getElementById("projectId"),
  projectTitle: document.getElementById("projectTitle"),
  featureSummary: document.getElementById("featureSummary"),
  uploadScreens: document.getElementById("uploadScreens"),
  uploadHtmlDesigns: document.getElementById("uploadHtmlDesigns"),
  importProjectBtn: document.getElementById("importProjectBtn"),
  importProjectInput: document.getElementById("importProjectInput"),
  screenList: document.getElementById("screenList"),
  screenImage: document.getElementById("screenImage"),
  screenFrame: document.getElementById("screenFrame"),
  stage: document.getElementById("stage"),
  overlayLayer: document.getElementById("overlayLayer"),
  draftRect: document.getElementById("draftRect"),
  emptyState: document.getElementById("emptyState"),
  statusBar: document.getElementById("statusBar"),
  annotationForm: document.getElementById("annotationForm"),
  annotationId: document.getElementById("annotationId"),
  annotationMode: document.getElementById("annotationMode"),
  easyFields: document.getElementById("easyFields"),
  detailedFields: document.getElementById("detailedFields"),
  easyCommand: document.getElementById("easyCommand"),
  easyDetail: document.getElementById("easyDetail"),
  label: document.getElementById("label"),
  description: document.getElementById("description"),
  interactionType: document.getElementById("interactionType"),
  expectedResult: document.getElementById("expectedResult"),
  targetScreenId: document.getElementById("targetScreenId"),
  componentHint: document.getElementById("componentHint"),
  developmentNotes: document.getElementById("developmentNotes"),
  priority: document.getElementById("priority"),
  saveBtn: document.getElementById("saveBtn"),
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
  return state.project.screens.find((screen) => screen.screen_id === state.currentScreenId) || null;
}

function currentRenderType() {
  return currentScreen()?.render_type === "html" ? "html" : "image";
}

function currentVisualSource(screen) {
  if (!screen) {
    return "";
  }
  return screen.design_path || screen.image_path || "";
}

function activeCanvasElement() {
  return currentRenderType() === "html" ? ui.screenFrame : ui.screenImage;
}

function hasRenderableCanvas() {
  const canvas = activeCanvasElement();
  if (!canvas) {
    return false;
  }
  const rect = canvas.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
}

function isTextEditingTarget(target) {
  if (!(target instanceof HTMLElement)) {
    return false;
  }
  return Boolean(target.closest("input, textarea, select, [contenteditable='true']"));
}

function showStatus(message, level = "info") {
  if (!ui.statusBar) {
    return;
  }
  ui.statusBar.textContent = message;
  ui.statusBar.dataset.level = level;
}

function updateDraftPreviewVisibility() {
  const showPreview = Boolean(state.draftRectNorm) && !state.editingAnnotationId;
  ui.draftRect.classList.toggle("hidden", !showPreview);
  if (showPreview) {
    updateDraftRect();
  }
}

function setModeRequired(container, required) {
  container.querySelectorAll("input, textarea, select").forEach((element) => {
    if (!(element instanceof HTMLElement)) {
      return;
    }
    if (required) {
      element.removeAttribute("disabled");
      if (element.dataset.requiredOriginal === "1") {
        element.setAttribute("required", "");
      }
    } else {
      if (element.hasAttribute("required")) {
        element.dataset.requiredOriginal = "1";
      }
      element.removeAttribute("required");
      element.setAttribute("disabled", "");
    }
  });
}

function applyAnnotationMode(mode) {
  const resolved = mode === "easy" ? "easy" : "detailed";
  ui.annotationMode.value = resolved;
  if (resolved === "easy") {
    ui.easyCommand.value = ui.easyCommand.value || ui.label.value;
    ui.easyDetail.value = ui.easyDetail.value || ui.description.value || ui.expectedResult.value;
    ui.easyFields.classList.remove("hidden");
    ui.detailedFields.classList.add("hidden");
    setModeRequired(ui.easyFields, true);
    setModeRequired(ui.detailedFields, false);
  } else {
    if (!ui.label.value && ui.easyCommand.value) {
      ui.label.value = ui.easyCommand.value;
    }
    if (!ui.description.value && ui.easyDetail.value) {
      ui.description.value = ui.easyDetail.value;
    }
    if (!ui.expectedResult.value && ui.easyDetail.value) {
      ui.expectedResult.value = ui.easyDetail.value;
    }
    if (!ui.componentHint.value) {
      ui.componentHint.value = "Command";
    }
    if (!ui.developmentNotes.value && ui.easyDetail.value) {
      ui.developmentNotes.value = ui.easyDetail.value;
    }
    ui.easyFields.classList.add("hidden");
    ui.detailedFields.classList.remove("hidden");
    setModeRequired(ui.easyFields, false);
    setModeRequired(ui.detailedFields, true);
  }
}

function updateProjectMeta() {
  state.project.project_id = ui.projectId.value.trim() || "project-ui-flow";
  state.project.project_title = ui.projectTitle.value.trim() || "UI Flow Annotation";
  state.project.feature_summary = ui.featureSummary.value.trim();
}

function syncProjectMetaFields() {
  ui.projectId.value = state.project.project_id;
  ui.projectTitle.value = state.project.project_title;
  ui.featureSummary.value = state.project.feature_summary || "";
}

function updateTargetSelect() {
  const previous = ui.targetScreenId.value;
  ui.targetScreenId.innerHTML = "<option value=\"\">None</option>";
  state.project.screens.forEach((screen) => {
    const option = document.createElement("option");
    option.value = screen.screen_id;
    option.textContent = `${screen.screen_title} (${screen.screen_id})`;
    ui.targetScreenId.appendChild(option);
  });
  if (state.project.screens.some((screen) => screen.screen_id === previous)) {
    ui.targetScreenId.value = previous;
  }
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

function setProject(project) {
  state.project = project;
  syncProjectMetaFields();
  renderScreenList();
  if (state.project.screens.length) {
    selectScreen(state.project.screens[0].screen_id);
  } else {
    selectScreen(null);
  }
}

function selectScreen(screenId) {
  state.currentScreenId = screenId;
  clearForm();

  const screen = currentScreen();
  if (!screen) {
    ui.emptyState.classList.remove("hidden");
    ui.screenImage.removeAttribute("src");
    ui.screenFrame.removeAttribute("src");
    ui.screenImage.classList.add("hidden");
    ui.screenFrame.classList.add("hidden");
    ui.overlayLayer.innerHTML = "";
    renderScreenList();
    return;
  }

  ui.emptyState.classList.add("hidden");
  const source = currentVisualSource(screen);
  if (screen.render_type === "html") {
    ui.screenImage.classList.add("hidden");
    ui.screenFrame.classList.remove("hidden");
    ui.screenImage.removeAttribute("src");
    ui.screenFrame.src = source;
  } else {
    ui.screenFrame.classList.add("hidden");
    ui.screenImage.classList.remove("hidden");
    ui.screenFrame.removeAttribute("src");
    ui.screenImage.src = source;
  }
  renderScreenList();
  renderOverlays();
}

function getImageMetrics() {
  const canvasRect = activeCanvasElement().getBoundingClientRect();
  const stageRect = ui.stage.getBoundingClientRect();
  return { canvasRect, stageRect };
}

function toNorm(clientX, clientY) {
  const { canvasRect } = getImageMetrics();
  const x = clamp((clientX - canvasRect.left) / canvasRect.width, 0, 1);
  const y = clamp((clientY - canvasRect.top) / canvasRect.height, 0, 1);
  return { x, y };
}

function updateDraftRect() {
  if (!state.draftRectNorm) {
    return;
  }
  const { canvasRect, stageRect } = getImageMetrics();
  const { x, y, width, height } = state.draftRectNorm;
  ui.draftRect.style.left = `${canvasRect.left - stageRect.left + x * canvasRect.width}px`;
  ui.draftRect.style.top = `${canvasRect.top - stageRect.top + y * canvasRect.height}px`;
  ui.draftRect.style.width = `${width * canvasRect.width}px`;
  ui.draftRect.style.height = `${height * canvasRect.height}px`;
}

function findAnnotation(annotationId) {
  const screen = currentScreen();
  if (!screen) {
    return null;
  }
  return screen.annotations.find((annotation) => annotation.annotation_id === annotationId) || null;
}

function beginDraw(event) {
  if (event.button !== 0 || !currentScreen()) {
    return;
  }
  if (!hasRenderableCanvas()) {
    return;
  }
  if (event.target instanceof Element && event.target.closest(".annotation-box")) {
    return;
  }

  const start = toNorm(event.clientX, event.clientY);
  state.interaction = {
    mode: "draw",
    startX: start.x,
    startY: start.y
  };
  state.editingAnnotationId = null;
  state.draftRectNorm = {
    x: start.x,
    y: start.y,
    width: 0,
    height: 0
  };
  updateDraftPreviewVisibility();
}

function beginMove(annotationId, event) {
  if (event.button !== 0) {
    return;
  }
  const annotation = findAnnotation(annotationId);
  if (!annotation) {
    return;
  }
  const start = toNorm(event.clientX, event.clientY);
  state.interaction = {
    mode: "move",
    annotationId,
    startX: start.x,
    startY: start.y,
    origin: {
      x: annotation.x,
      y: annotation.y,
      width: annotation.width,
      height: annotation.height
    }
  };
  loadAnnotation(annotationId);
}

function beginResize(annotationId, event) {
  if (event.button !== 0) {
    return;
  }
  const annotation = findAnnotation(annotationId);
  if (!annotation) {
    return;
  }
  const start = toNorm(event.clientX, event.clientY);
  state.interaction = {
    mode: "resize",
    annotationId,
    startX: start.x,
    startY: start.y,
    origin: {
      x: annotation.x,
      y: annotation.y,
      width: annotation.width,
      height: annotation.height
    }
  };
  loadAnnotation(annotationId);
  event.stopPropagation();
  event.preventDefault();
}

function movePointer(event) {
  if (!state.interaction) {
    return;
  }

  if (state.interaction.mode === "draw") {
    const point = toNorm(event.clientX, event.clientY);
    const left = Math.min(state.interaction.startX, point.x);
    const top = Math.min(state.interaction.startY, point.y);
    const width = Math.abs(state.interaction.startX - point.x);
    const height = Math.abs(state.interaction.startY - point.y);
    state.draftRectNorm = { x: left, y: top, width, height };
    updateDraftRect();
    return;
  }

  const annotation = findAnnotation(state.interaction.annotationId);
  if (!annotation) {
    state.interaction = null;
    return;
  }

  const point = toNorm(event.clientX, event.clientY);
  const dx = point.x - state.interaction.startX;
  const dy = point.y - state.interaction.startY;

  if (state.interaction.mode === "move") {
    annotation.x = +clamp(state.interaction.origin.x + dx, 0, 1 - annotation.width).toFixed(4);
    annotation.y = +clamp(state.interaction.origin.y + dy, 0, 1 - annotation.height).toFixed(4);
  } else if (state.interaction.mode === "resize") {
    annotation.width = +clamp(state.interaction.origin.width + dx, MIN_RECT_SIZE, 1 - annotation.x).toFixed(4);
    annotation.height = +clamp(state.interaction.origin.height + dy, MIN_RECT_SIZE, 1 - annotation.y).toFixed(4);
  }

  if (annotation.annotation_id === state.editingAnnotationId) {
    state.draftRectNorm = {
      x: annotation.x,
      y: annotation.y,
      width: annotation.width,
      height: annotation.height
    };
    updateDraftRect();
  }
  renderOverlays();
}

function stopPointer() {
  if (!state.interaction) {
    return;
  }

  if (state.interaction.mode === "draw") {
    const rect = state.draftRectNorm;
    state.interaction = null;

    if (!rect || rect.width < MIN_RECT_SIZE || rect.height < MIN_RECT_SIZE) {
      state.draftRectNorm = null;
      updateDraftPreviewVisibility();
      showStatus("Region ignored: draw a larger rectangle.", "warn");
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
    updateDraftPreviewVisibility();
    ui.label.focus();
    showStatus("Region selected. Fill fields and save.", "info");
    return;
  }

  state.interaction = null;
}

function renderOverlays() {
  const screen = currentScreen();
  ui.overlayLayer.innerHTML = "";
  if (!screen || !hasRenderableCanvas()) {
    return;
  }

  const { canvasRect, stageRect } = getImageMetrics();
  screen.annotations.forEach((annotation) => {
    const box = document.createElement("div");
    box.className = `annotation-box${annotation.annotation_id === state.editingAnnotationId ? " active" : ""}`;
    box.style.left = `${canvasRect.left - stageRect.left + annotation.x * canvasRect.width}px`;
    box.style.top = `${canvasRect.top - stageRect.top + annotation.y * canvasRect.height}px`;
    box.style.width = `${annotation.width * canvasRect.width}px`;
    box.style.height = `${annotation.height * canvasRect.height}px`;
    box.title = annotation.annotation_id;

    const label = document.createElement("span");
    label.className = "annotation-label";
    label.textContent = annotation.label;
    box.appendChild(label);

    const resizeHandle = document.createElement("button");
    resizeHandle.type = "button";
    resizeHandle.className = "annotation-resize-handle";
    resizeHandle.setAttribute("aria-label", `Resize ${annotation.label}`);
    resizeHandle.addEventListener("mousedown", (event) => beginResize(annotation.annotation_id, event));
    box.appendChild(resizeHandle);

    box.addEventListener("click", (event) => {
      event.stopPropagation();
      loadAnnotation(annotation.annotation_id);
    });
    box.addEventListener("mousedown", (event) => {
      if (!(event.target instanceof Element) || !event.target.classList.contains("annotation-resize-handle")) {
        event.stopPropagation();
        beginMove(annotation.annotation_id, event);
      }
    });

    ui.overlayLayer.appendChild(box);
  });
}

function loadAnnotation(annotationId) {
  const annotation = findAnnotation(annotationId);
  if (!annotation) {
    return;
  }

  state.editingAnnotationId = annotationId;
  state.draftRectNorm = {
    x: annotation.x,
    y: annotation.y,
    width: annotation.width,
    height: annotation.height
  };

  ui.annotationId.value = annotation.annotation_id;
  ui.easyCommand.value = annotation.label;
  ui.easyDetail.value = annotation.description || annotation.expected_result || annotation.development_notes || "";
  ui.label.value = annotation.label;
  ui.description.value = annotation.description;
  ui.interactionType.value = annotation.interaction_type;
  ui.expectedResult.value = annotation.expected_result;
  ui.targetScreenId.value = annotation.target_screen_id || "";
  ui.componentHint.value = annotation.component_hint;
  ui.developmentNotes.value = annotation.development_notes;
  ui.priority.value = annotation.priority;
  ui.deleteBtn.disabled = false;
  applyAnnotationMode(annotation.annotation_mode || "detailed");
  updateDraftPreviewVisibility();
  renderOverlays();
}

function clearForm() {
  state.editingAnnotationId = null;
  state.draftRectNorm = null;
  ui.annotationId.value = "";
  ui.annotationForm.reset();
  ui.easyCommand.value = "";
  ui.easyDetail.value = "";
  ui.interactionType.value = "click";
  ui.priority.value = "medium";
  ui.targetScreenId.value = "";
  ui.deleteBtn.disabled = true;
  applyAnnotationMode(ui.annotationMode.value);
  updateDraftPreviewVisibility();
  renderOverlays();
}

function handleImageUpload(event) {
  const files = Array.from(event.target.files || []);
  files.forEach((file) => {
    const screenId = genId("screen");
    const source = URL.createObjectURL(file);
    state.project.screens.push({
      render_type: "image",
      screen_id: screenId,
      screen_title: file.name.replace(/\.[^.]+$/, ""),
      design_path: source,
      image_path: source,
      screen_notes: "",
      annotations: []
    });
  });

  renderScreenList();
  if (!state.currentScreenId && state.project.screens.length) {
    selectScreen(state.project.screens[0].screen_id);
  } else {
    renderOverlays();
  }
  if (files.length) {
    showStatus(`Uploaded ${files.length} image screen(s).`, "success");
  }
}

function handleHtmlUpload(event) {
  const files = Array.from(event.target.files || []);
  files.forEach((file) => {
    const screenId = genId("screen");
    const source = URL.createObjectURL(file);
    state.project.screens.push({
      render_type: "html",
      screen_id: screenId,
      screen_title: file.name.replace(/\.[^.]+$/, ""),
      design_path: source,
      image_path: source,
      screen_notes: "",
      annotations: []
    });
  });

  renderScreenList();
  if (!state.currentScreenId && state.project.screens.length) {
    selectScreen(state.project.screens[0].screen_id);
  } else {
    renderOverlays();
  }
  if (files.length) {
    showStatus(`Opened ${files.length} HTML design file(s).`, "success");
  }
}

function saveAnnotation(event) {
  event.preventDefault();
  const screen = currentScreen();
  if (!screen || !state.draftRectNorm) {
    showStatus("Draw a region before saving.", "error");
    alert("Draw a region on the screenshot before saving.");
    return;
  }

  const mode = ui.annotationMode.value === "easy" ? "easy" : "detailed";
  const existing = state.editingAnnotationId ? findAnnotation(state.editingAnnotationId) : null;
  const annotationId = state.editingAnnotationId || genId("ann");

  let annotation;
  if (mode === "easy") {
    const command = ui.easyCommand.value.trim();
    const detail = ui.easyDetail.value.trim();
    annotation = {
      annotation_id: annotationId,
      label: command,
      x: +state.draftRectNorm.x.toFixed(4),
      y: +state.draftRectNorm.y.toFixed(4),
      width: +state.draftRectNorm.width.toFixed(4),
      height: +state.draftRectNorm.height.toFixed(4),
      interaction_type: existing?.interaction_type || "click",
      description: detail,
      expected_result: existing?.expected_result || detail,
      target_screen_id: existing?.target_screen_id || null,
      component_hint: existing?.component_hint || "Command",
      development_notes: detail || existing?.development_notes || "Simple annotation detail.",
      priority: existing?.priority || "medium",
      annotation_mode: "easy"
    };
  } else {
    annotation = {
      annotation_id: annotationId,
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
      priority: ui.priority.value,
      annotation_mode: "detailed"
    };
  }

  const existingIndex = screen.annotations.findIndex((item) => item.annotation_id === annotation.annotation_id);
  if (existingIndex >= 0) {
    screen.annotations[existingIndex] = annotation;
  } else {
    screen.annotations.push(annotation);
  }

  state.editingAnnotationId = annotation.annotation_id;
  ui.annotationId.value = annotation.annotation_id;
  ui.deleteBtn.disabled = false;
  updateDraftPreviewVisibility();
  renderScreenList();
  renderOverlays();
  showStatus(`Saved annotation ${annotation.annotation_id}.`, "success");
}

function deleteAnnotation() {
  const screen = currentScreen();
  if (!screen || !state.editingAnnotationId) {
    return;
  }
  const deletedId = state.editingAnnotationId;
  screen.annotations = screen.annotations.filter((annotation) => annotation.annotation_id !== state.editingAnnotationId);
  clearForm();
  renderScreenList();
  showStatus(`Deleted annotation ${deletedId}.`, "warn");
}

function buildExportModel() {
  updateProjectMeta();
  return buildExportModelFromProject(state.project);
}

function download(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function applyImportedProject(rawProject, options = {}) {
  const validation = validateImportProject(rawProject);
  if (!validation.valid) {
    const preview = validation.errors.slice(0, 10).map((error) => `- ${error}`).join("\n");
    const suffix = validation.errors.length > 10 ? "\n- ...more errors omitted" : "";
    const message = `Import failed. Fix the project JSON:\n${preview}${suffix}`;
    showStatus("Import failed. Review schema errors.", "error");
    alert(message);
    return false;
  }

  const normalized = normalizeImportedProject(rawProject, options);
  setProject(normalized);
  showStatus(`Imported project "${normalized.project_title}".`, "success");
  return true;
}

async function handleImportProjectFile(event) {
  const file = event.target.files?.[0];
  if (!file) {
    return;
  }

  try {
    const text = await file.text();
    const data = JSON.parse(text);
    applyImportedProject(data);
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    showStatus("Import failed due to invalid JSON.", "error");
    alert(`Import failed. The file is not valid JSON.\n\n${reason}`);
  } finally {
    ui.importProjectInput.value = "";
  }
}

function selectAdjacentScreen(step) {
  if (!state.project.screens.length) {
    return;
  }
  const currentIndex = state.project.screens.findIndex((screen) => screen.screen_id === state.currentScreenId);
  const base = currentIndex >= 0 ? currentIndex : 0;
  const nextIndex = (base + step + state.project.screens.length) % state.project.screens.length;
  selectScreen(state.project.screens[nextIndex].screen_id);
  showStatus(`Selected screen: ${state.project.screens[nextIndex].screen_title}.`, "info");
}

function selectAdjacentAnnotation(step) {
  const screen = currentScreen();
  if (!screen || !screen.annotations.length) {
    return;
  }
  const currentIndex = screen.annotations.findIndex((annotation) => annotation.annotation_id === state.editingAnnotationId);
  const base = currentIndex >= 0 ? currentIndex : step > 0 ? -1 : 0;
  const nextIndex = (base + step + screen.annotations.length) % screen.annotations.length;
  loadAnnotation(screen.annotations[nextIndex].annotation_id);
  showStatus(`Selected annotation: ${screen.annotations[nextIndex].label}.`, "info");
}

function handleKeydown(event) {
  const typing = isTextEditingTarget(event.target);
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
    event.preventDefault();
    if (currentScreen()) {
      ui.annotationForm.requestSubmit();
    }
    return;
  }

  if (!typing && (event.key === "Delete" || event.key === "Backspace")) {
    if (state.editingAnnotationId) {
      event.preventDefault();
      deleteAnnotation();
    }
    return;
  }

  if (event.key === "Escape") {
    if (!typing || state.editingAnnotationId || state.draftRectNorm) {
      event.preventDefault();
      clearForm();
      showStatus("Selection cleared.", "info");
    }
    return;
  }

  if (!typing && event.key === "]") {
    event.preventDefault();
    selectAdjacentScreen(1);
    return;
  }

  if (!typing && event.key === "[") {
    event.preventDefault();
    selectAdjacentScreen(-1);
    return;
  }

  if (!typing && event.key === "ArrowDown") {
    event.preventDefault();
    selectAdjacentAnnotation(1);
    return;
  }

  if (!typing && event.key === "ArrowUp") {
    event.preventDefault();
    selectAdjacentAnnotation(-1);
  }
}

async function loadDemoProjectIfNeeded() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("demo") !== "1") {
    return;
  }
  try {
    const response = await fetch("../../references/annotation-export-example.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    const loaded = applyImportedProject(data, { imageBasePath: "../../" });
    if (loaded) {
      showStatus("Demo project loaded. Start editing or export now.", "success");
    }
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    showStatus(`Demo load failed: ${reason}`, "error");
  }
}

ui.projectId.addEventListener("input", updateProjectMeta);
ui.projectTitle.addEventListener("input", updateProjectMeta);
ui.featureSummary.addEventListener("input", updateProjectMeta);
ui.uploadScreens.addEventListener("change", handleImageUpload);
ui.uploadHtmlDesigns.addEventListener("change", handleHtmlUpload);
ui.importProjectBtn.addEventListener("click", () => ui.importProjectInput.click());
ui.importProjectInput.addEventListener("change", handleImportProjectFile);
ui.annotationMode.addEventListener("change", () => {
  applyAnnotationMode(ui.annotationMode.value);
  showStatus(`Annotation mode: ${ui.annotationMode.value}.`, "info");
});
ui.annotationForm.addEventListener("submit", saveAnnotation);
ui.deleteBtn.addEventListener("click", deleteAnnotation);
ui.clearBtn.addEventListener("click", () => {
  clearForm();
  showStatus("Selection cleared.", "info");
});
ui.exportJsonBtn.addEventListener("click", () => {
  const project = buildExportModel();
  download(`${project.project_id}.json`, JSON.stringify(project, null, 2), "application/json");
  showStatus("JSON export downloaded.", "success");
});
ui.exportMdBtn.addEventListener("click", () => {
  const project = buildExportModel();
  download(`${project.project_id}.md`, toMarkdown(project), "text/markdown");
  showStatus("Markdown export downloaded.", "success");
});

ui.stage.addEventListener("mousedown", beginDraw);
window.addEventListener("mousemove", movePointer);
window.addEventListener("mouseup", stopPointer);
window.addEventListener("resize", () => {
  updateDraftRect();
  renderOverlays();
});
ui.screenImage.addEventListener("load", renderOverlays);
ui.screenFrame.addEventListener("load", renderOverlays);
window.addEventListener("keydown", handleKeydown);

updateProjectMeta();
applyAnnotationMode("detailed");
showStatus("Ready. Upload image/HTML screens or import a JSON project.", "info");
loadDemoProjectIfNeeded();
