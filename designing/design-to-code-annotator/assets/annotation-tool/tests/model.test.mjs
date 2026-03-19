import test from "node:test";
import assert from "node:assert/strict";

import {
  buildExportModelFromProject,
  normalizeImportedProject,
  toMarkdown,
  validateImportProject
} from "../model.js";

function makeProject() {
  return {
    project_id: "demo-flow",
    project_title: "Demo Flow",
    feature_summary: "Demo summary",
    screens: [
      {
        screen_id: "screen_a",
        screen_title: "Screen A",
        image_path: "references/examples/screens/screen-login.svg",
        screen_notes: "",
        annotations: [
          {
            annotation_id: "ann_submit",
            label: "Submit",
            x: 0.2,
            y: 0.3,
            width: 0.4,
            height: 0.1,
            interaction_type: "submit",
            description: "Submit form.",
            expected_result: "Navigate to B.",
            target_screen_id: "screen_b",
            component_hint: "PrimaryButton",
            development_notes: "Disable when loading.",
            priority: "high"
          }
        ]
      },
      {
        screen_id: "screen_b",
        screen_title: "Screen B",
        image_path: "references/examples/screens/screen-dashboard.svg",
        screen_notes: "",
        annotations: []
      }
    ],
    links: []
  };
}

test("validateImportProject accepts a valid multi-screen project", () => {
  const result = validateImportProject(makeProject());
  assert.equal(result.valid, true);
  assert.deepEqual(result.errors, []);
});

test("validateImportProject reports missing required fields", () => {
  const invalid = makeProject();
  delete invalid.screens[0].annotations[0].description;
  const result = validateImportProject(invalid);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.includes("description")));
});

test("buildExportModelFromProject recomputes linked transitions", () => {
  const exported = buildExportModelFromProject(makeProject());
  assert.equal(exported.links.length, 1);
  assert.equal(exported.links[0].from_screen_id, "screen_a");
  assert.equal(exported.links[0].to_screen_id, "screen_b");
});

test("toMarkdown includes navigation flow entries", () => {
  const exported = buildExportModelFromProject(makeProject());
  const markdown = toMarkdown(exported);
  assert.match(markdown, /## 4\. Navigation Flow/);
  assert.match(markdown, /screen_a\.ann_submit/);
  assert.match(markdown, /-> `screen_b`/);
});

test("normalizeImportedProject resolves relative image paths for demos", () => {
  const normalized = normalizeImportedProject(makeProject(), { imageBasePath: "../../" });
  assert.equal(
    normalized.screens[0].image_path,
    "../../references/examples/screens/screen-login.svg"
  );
});

test("normalizeImportedProject keeps html render mode and design path", () => {
  const project = makeProject();
  project.screens[0].render_type = "html";
  project.screens[0].design_path = "references/examples/html/price-intelligence-mvp-v1.html";
  const normalized = normalizeImportedProject(project, { imageBasePath: "../../" });
  assert.equal(normalized.screens[0].render_type, "html");
  assert.equal(
    normalized.screens[0].design_path,
    "../../references/examples/html/price-intelligence-mvp-v1.html"
  );
});
