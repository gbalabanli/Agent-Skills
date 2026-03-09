const sourceText = document.querySelector("#sourceText");
const analyzeButton = document.querySelector("#analyzeButton");
const humanizeButton = document.querySelector("#humanizeButton");
const clearButton = document.querySelector("#clearButton");

const localScore = document.querySelector("#localScore");
const localVerdict = document.querySelector("#localVerdict");
const confidenceScore = document.querySelector("#confidenceScore");
const confidenceLabel = document.querySelector("#confidenceLabel");
const wordCount = document.querySelector("#wordCount");
const sentenceCount = document.querySelector("#sentenceCount");
const highlights = document.querySelector("#highlights");
const patternTable = document.querySelector("#patternTable");
const notes = document.querySelector("#notes");
const liveConfidence = document.querySelector("#liveConfidence");
const modelUsed = document.querySelector("#modelUsed");
const reportId = document.querySelector("#reportId");
const expiresAt = document.querySelector("#expiresAt");
const summaryText = document.querySelector("#summaryText");
const humanizedText = document.querySelector("#humanizedText");
const baselineScore = document.querySelector("#baselineScore");
const finalScore = document.querySelector("#finalScore");
const retryLog = document.querySelector("#retryLog");
const quillbotLiveScore = document.querySelector("#quillbotLiveScore");
const quillbotVerdict = document.querySelector("#quillbotVerdict");
const quillbotModel = document.querySelector("#quillbotModel");
const quillbotReportId = document.querySelector("#quillbotReportId");
const quillbotHumanParaphrased = document.querySelector("#quillbotHumanParaphrased");
const quillbotAiParaphrased = document.querySelector("#quillbotAiParaphrased");
const quillbotTimeout = document.querySelector("#quillbotTimeout");
const quillbotTable = document.querySelector("#quillbotTable");
const scribbrLiveScore = document.querySelector("#scribbrLiveScore");
const scribbrVerdict = document.querySelector("#scribbrVerdict");
const scribbrModel = document.querySelector("#scribbrModel");
const scribbrReportId = document.querySelector("#scribbrReportId");
const scribbrHumanParaphrased = document.querySelector("#scribbrHumanParaphrased");
const scribbrAiParaphrased = document.querySelector("#scribbrAiParaphrased");
const scribbrTimeout = document.querySelector("#scribbrTimeout");
const scribbrTable = document.querySelector("#scribbrTable");

const externalInputs = [
  document.querySelector("#copyleaksScore"),
];
const externalAverage = document.querySelector("#externalAverage");
const scoreSpread = document.querySelector("#scoreSpread");

let currentLocalScore = 0;
let currentQuillbotScore = null;
let currentScribbrScore = null;

function clampScore(value) {
  if (Number.isNaN(value)) {
    return null;
  }
  return Math.max(0, Math.min(100, value));
}

function renderList(element, items, emptyMessage) {
  element.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = emptyMessage;
    element.appendChild(li);
    return;
  }

  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  }
}

function renderTable(rows) {
  patternTable.innerHTML = "";
  if (!rows.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.textContent = "No sentence breakdown returned for this sample.";
    row.appendChild(cell);
    patternTable.appendChild(row);
    return;
  }

  for (const item of rows) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.index + 1}</td>
      <td>${item.ai_probability.toFixed(1)}%</td>
      <td>${item.verdict}</td>
    `;
    row.title = `${item.text}\n\n${item.reason}`;
    patternTable.appendChild(row);
  }
}

function renderChunkTable(element, rows, emptyMessage) {
  element.innerHTML = "";
  if (!rows.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.textContent = emptyMessage;
    row.appendChild(cell);
    element.appendChild(row);
    return;
  }

  rows.forEach((item, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${item.ai_probability.toFixed(1)}%</td>
      <td>${item.type || "Unknown"}</td>
    `;
    row.title = item.text || "";
    element.appendChild(row);
  });
}

function updateExternalComparison() {
  const values = externalInputs
    .map((input) => clampScore(Number.parseFloat(input.value)))
    .filter((value) => value !== null);

  if (currentQuillbotScore !== null) {
    values.push(currentQuillbotScore);
  }
  if (currentScribbrScore !== null) {
    values.push(currentScribbrScore);
  }

  if (!values.length) {
    externalAverage.textContent = "-";
    scoreSpread.textContent = "-";
    return;
  }

  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  const delta = average - currentLocalScore;

  externalAverage.textContent = `${average.toFixed(1)}%`;
  if (currentLocalScore === 0 && !sourceText.value.trim()) {
    scoreSpread.textContent = "Analyze text first";
    return;
  }

  const prefix = delta > 0 ? "+" : "";
  scoreSpread.textContent = `${prefix}${delta.toFixed(1)} pts`;
}

function resetResultState() {
  currentLocalScore = 0;
  currentQuillbotScore = null;
  currentScribbrScore = null;
  localScore.textContent = "0";
  localVerdict.textContent = "No text";
  confidenceScore.textContent = "0";
  confidenceLabel.textContent = "No text";
  wordCount.textContent = "0";
  sentenceCount.textContent = "0";
  liveConfidence.textContent = "-";
  modelUsed.textContent = "-";
  reportId.textContent = "-";
  expiresAt.textContent = "-";
  summaryText.textContent = "Run an analysis to fetch the detector summary.";
  humanizedText.value = "";
  baselineScore.textContent = "-";
  finalScore.textContent = "-";
  quillbotLiveScore.textContent = "-";
  quillbotVerdict.textContent = "Not fetched yet";
  quillbotModel.textContent = "-";
  quillbotReportId.textContent = "No report";
  quillbotHumanParaphrased.textContent = "-";
  quillbotAiParaphrased.textContent = "-";
  quillbotTimeout.textContent = "No timeout data";
  scribbrLiveScore.textContent = "-";
  scribbrVerdict.textContent = "Not fetched yet";
  scribbrModel.textContent = "-";
  scribbrReportId.textContent = "No report";
  scribbrHumanParaphrased.textContent = "-";
  scribbrAiParaphrased.textContent = "-";
  scribbrTimeout.textContent = "No timeout data";
  renderList(highlights, [], "Run an analysis to see detector notes.");
  renderList(notes, ["This panel shows metadata returned by the live detector call."], "");
  renderList(retryLog, ["No retry run yet."], "");
  renderTable([]);
  renderChunkTable(quillbotTable, [], "No QuillBot chunk breakdown returned for this sample.");
  renderChunkTable(scribbrTable, [], "No Scribbr chunk breakdown returned for this sample.");
}

async function analyzeText() {
  const text = sourceText.value.trim();
  if (!text) {
    resetResultState();
    updateExternalComparison();
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.textContent = "Analyzing...";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Analysis failed with status ${response.status}`);
    }

    const data = await response.json();
    currentLocalScore = data.score;
    localScore.textContent = `${data.score.toFixed(1)}%`;
    localVerdict.textContent = data.verdict;
    confidenceScore.textContent = `${data.human_score.toFixed(1)}%`;
    confidenceLabel.textContent = "Human probability";
    wordCount.textContent = String(data.word_count);
    sentenceCount.textContent = String(data.sentence_count);
    liveConfidence.textContent = data.confidence_label || "-";
    modelUsed.textContent = data.model_used || "-";
    reportId.textContent = data.report_id === null ? "-" : String(data.report_id);
    expiresAt.textContent = data.expires_at || "-";
    summaryText.textContent = data.summary || "No summary returned.";
    renderList(highlights, data.sentences.map((item) => `Sentence ${item.index + 1}: ${item.ai_probability.toFixed(1)}% AI, ${item.reason}`), "No sentence notes returned.");
    renderList(notes, data.notes, "No notes.");
    renderTable(data.sentences);

    const quillbot = data.quillbot;
    currentQuillbotScore = quillbot ? quillbot.score : null;
    quillbotLiveScore.textContent = quillbot ? `${quillbot.score.toFixed(1)}%` : "-";
    quillbotVerdict.textContent = quillbot?.verdict || "Unavailable";
    quillbotModel.textContent = quillbot?.model_version || "-";
    quillbotReportId.textContent = quillbot?.report_id ? `Report ${quillbot.report_id}` : "No report";
    quillbotHumanParaphrased.textContent = quillbot ? `${quillbot.human_paraphrased_score.toFixed(1)}%` : "-";
    quillbotAiParaphrased.textContent = quillbot ? `${quillbot.ai_paraphrased_score.toFixed(1)}%` : "-";
    quillbotTimeout.textContent = quillbot ? (quillbot.timed_out ? "Timed out" : "Completed") : "No timeout data";
    renderChunkTable(quillbotTable, quillbot?.chunks || [], "No QuillBot chunk breakdown returned for this sample.");

    const scribbr = data.scribbr;
    currentScribbrScore = scribbr ? scribbr.score : null;
    scribbrLiveScore.textContent = scribbr ? `${scribbr.score.toFixed(1)}%` : "-";
    scribbrVerdict.textContent = scribbr?.verdict || "Unavailable";
    scribbrModel.textContent = scribbr?.model_version || "-";
    scribbrReportId.textContent = scribbr?.report_id ? `Report ${scribbr.report_id}` : "No report";
    scribbrHumanParaphrased.textContent = scribbr ? `${scribbr.human_paraphrased_score.toFixed(1)}%` : "-";
    scribbrAiParaphrased.textContent = scribbr ? `${scribbr.ai_paraphrased_score.toFixed(1)}%` : "-";
    scribbrTimeout.textContent = scribbr ? (scribbr.timed_out ? "Timed out" : "Completed") : "No timeout data";
    renderChunkTable(scribbrTable, scribbr?.chunks || [], "No Scribbr chunk breakdown returned for this sample.");

    updateExternalComparison();
  } catch (error) {
    resetResultState();
    renderList(notes, [error.message], "No notes.");
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analyze text";
  }
}

function formatRetryEntry(item) {
  const diagnosis = (item.diagnosis || []).join(", ");
  const delta = item.improved_vs_best;
  const prefix = delta > 0 ? "+" : "";
  return `Attempt ${item.attempt}: score ${item.candidate_score.toFixed(1)}% (${prefix}${delta.toFixed(1)} vs best), diagnosis: ${diagnosis}`;
}

async function humanizeAndRecheck() {
  const text = sourceText.value.trim();
  if (!text) {
    resetResultState();
    updateExternalComparison();
    return;
  }

  humanizeButton.disabled = true;
  humanizeButton.textContent = "Humanizing...";

  try {
    const response = await fetch("/api/humanize-retry", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text, max_attempts: 3 }),
    });

    if (!response.ok) {
      throw new Error(`Humanize retry failed with status ${response.status}`);
    }

    const data = await response.json();
    const baseline = data.baseline_analysis || {};
    const final = data.final_analysis || {};

    baselineScore.textContent = baseline.score !== undefined ? `${Number(baseline.score).toFixed(1)}%` : "-";
    finalScore.textContent = final.score !== undefined ? `${Number(final.score).toFixed(1)}%` : "-";
    humanizedText.value = data.humanized_text || "";
    renderList(
      retryLog,
      (data.attempts || []).map(formatRetryEntry),
      "No retry attempts returned.",
    );

    if (data.humanized_text) {
      sourceText.value = data.humanized_text;
      await analyzeText();
    }
  } catch (error) {
    renderList(retryLog, [error.message], "No retry logs.");
  } finally {
    humanizeButton.disabled = false;
    humanizeButton.textContent = "Humanize + Recheck";
  }
}

function clearForm() {
  sourceText.value = "";
  resetResultState();
  for (const input of externalInputs) {
    input.value = "";
  }
  updateExternalComparison();
}

analyzeButton.addEventListener("click", analyzeText);
humanizeButton.addEventListener("click", humanizeAndRecheck);
clearButton.addEventListener("click", clearForm);
for (const input of externalInputs) {
  input.addEventListener("input", updateExternalComparison);
}

resetResultState();
