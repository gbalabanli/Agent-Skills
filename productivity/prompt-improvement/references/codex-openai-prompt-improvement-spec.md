# Codex + OpenAI Prompt Improvement Spec

<document_meta>
  <purpose>Transform weak prompts into high-performance prompts for OpenAI/Codex workflows.</purpose>
  <primary_user>LLM agent used inside a skill</primary_user>
  <last_updated>2026-03-05</last_updated>
  <source_policy>Prefer official OpenAI docs and cookbook patterns.</source_policy>
</document_meta>

## 1) Operating Contract

Use this document when a user provides a draft prompt and asks for a better version.

<operating_contract>
  <goal>Improve output quality while preserving user intent.</goal>
  <non_goal>Do not change task scope unless user explicitly asks.</non_goal>
  <style>Clear, compact, actionable, testable.</style>
  <priority_order>
    <item>Correctness</item>
    <item>Instruction clarity</item>
    <item>Output format reliability</item>
    <item>Cost/latency efficiency</item>
  </priority_order>
</operating_contract>

## 2) Prompt Rewrite Pipeline

<rewrite_pipeline>
  <step id="1">Classify prompt type: coding, reasoning, extraction, research, general.</step>
  <step id="2">Extract hard constraints: must-have outputs, forbidden actions, tools, budget/time limits, formatting rules.</step>
  <step id="3">Identify missing essentials: role, objective, context, constraints, validation, output schema.</step>
  <step id="4">Rewrite with explicit sections and XML delimiters.</step>
  <step id="5">Add verification instructions appropriate to task type.</step>
  <step id="6">Run quality checks (Section 7) before returning final prompt.</step>
</rewrite_pipeline>

## 3) Core Rules (Model-Agnostic)

<core_rules>
  <rule>Use explicit role + objective.</rule>
  <rule>State constraints concretely (length, format, scope, tools, deadlines).</rule>
  <rule>Use delimiters (XML tags/sections) to reduce ambiguity.</rule>
  <rule>Define output shape exactly (bullets, JSON schema, sections, file list).</rule>
  <rule>Ask for validation checks (tests, lint, sanity checks, citation checks) when relevant.</rule>
  <rule>Prefer zero-shot first; add few-shot examples only when output quality is unstable.</rule>
  <rule>Avoid unnecessary "think step by step" instructions for reasoning models.</rule>
</core_rules>

## 4) Model-Specific Steer

<model_steer>
  <gpt_models>
    <guidance>Be explicit about task execution details and output format.</guidance>
    <guidance>Use concise constraints for verbosity and structure.</guidance>
  </gpt_models>
  <reasoning_models>
    <guidance>Keep prompts direct; prioritize desired outcome and constraints.</guidance>
    <guidance>Avoid forcing chain-of-thought exposition.</guidance>
  </reasoning_models>
  <codex_models>
    <guidance>Include reproduction/validation steps and expected checks.</guidance>
    <guidance>Break large work into scoped phases when possible.</guidance>
    <guidance>State code quality bar (tests, lint, minimal diffs, no unnecessary churn).</guidance>
  </codex_models>
</model_steer>

## 5) Canonical XML Prompt Template

Use this as the default improved prompt output.

```xml
<prompt>
  <role>You are a senior {domain} assistant.</role>
  <objective>{single-sentence objective}</objective>

  <context>
    {relevant background}
  </context>

  <inputs>
    <input name="primary">{user task input}</input>
    <input name="artifacts">{files, logs, URLs, data if any}</input>
  </inputs>

  <constraints>
    <scope>{what to include and exclude}</scope>
    <quality_bar>{correctness, safety, maintainability requirements}</quality_bar>
    <latency_or_cost>{if specified}</latency_or_cost>
    <style>{tone/verbosity formatting expectations}</style>
  </constraints>

  <execution_rules>
    <rule>Do not change user intent.</rule>
    <rule>If information is missing, make minimal reasonable assumptions and state them.</rule>
    <rule>Prefer concise, high-signal output.</rule>
  </execution_rules>

  <output_format>
    <section name="result">{final answer/artifact}</section>
    <section name="changes_or_reasoning_summary">{brief explanation}</section>
    <section name="verification">{tests/checks/citations performed}</section>
    <section name="open_items">{optional unknowns or risks}</section>
  </output_format>
</prompt>
```

## 6) Task-Specific Templates

### 6.1 Coding / Codex Template

```xml
<prompt>
  <role>You are an autonomous senior software engineer.</role>
  <objective>{implement/fix/refactor objective}</objective>
  <context>{stack, repo constraints, acceptance criteria}</context>
  <constraints>
    <scope>Only requested changes. No unrelated refactors.</scope>
    <quality_bar>Production-safe code, minimal diff, strong type safety.</quality_bar>
  </constraints>
  <verification>
    <required>Run tests relevant to changed behavior.</required>
    <required>Run lint/type checks if available.</required>
    <required>Report exact files changed and validation results.</required>
  </verification>
  <output_format>
    <section name="plan">Short actionable plan.</section>
    <section name="implementation">Patch-ready changes.</section>
    <section name="validation">Commands run + outcomes.</section>
    <section name="risks">Known risks and rollback notes.</section>
  </output_format>
</prompt>
```

### 6.2 Research Template

```xml
<prompt>
  <role>You are an expert research assistant.</role>
  <objective>{research question}</objective>
  <constraints>
    <rule>Use reliable sources and cite factual claims.</rule>
    <rule>Resolve contradictions explicitly when sources disagree.</rule>
    <rule>Do not ask clarifying questions; cover plausible interpretations.</rule>
  </constraints>
  <output_format>
    <section name="summary">2-4 concise paragraphs.</section>
    <section name="findings">Grouped by sub-question.</section>
    <section name="recommendations">Prioritized actions.</section>
    <section name="sources">Clickable references with date and URL.</section>
  </output_format>
</prompt>
```

### 6.3 Structured Extraction Template

```xml
<prompt>
  <role>You are a structured data extraction assistant.</role>
  <objective>Extract fields from the provided content.</objective>
  <schema>
    {exact JSON schema here}
  </schema>
  <constraints>
    <rule>If unknown, return null (never guess).</rule>
    <rule>No extra keys outside schema.</rule>
  </constraints>
  <output_format>
    <section name="json_only">Return valid JSON only.</section>
  </output_format>
</prompt>
```

## 7) Quality Checks for the Improved Prompt

Return the improved prompt only after passing all checks:

<quality_checks>
  <check id="Q1">Intent preserved (no scope drift).</check>
  <check id="Q2">Objective and output format are explicit.</check>
  <check id="Q3">Constraints are testable, not vague.</check>
  <check id="Q4">Includes validation expectations where relevant.</check>
  <check id="Q5">Token-efficient wording (no redundant prose).</check>
</quality_checks>

Scoring rubric (0-2 each, target >= 8/10):
- Intent fidelity
- Constraint clarity
- Format specificity
- Verification strength
- Conciseness

## 8) Before/After Example

### Input (weak)

```text
fix my API code and make it better
```

### Output (improved)

```xml
<prompt>
  <role>You are a senior backend engineer.</role>
  <objective>Fix the API bug and improve reliability without changing public behavior.</objective>
  <context>The service is production-facing and backward compatibility is required.</context>
  <constraints>
    <scope>Only edit files needed for root-cause fix and related tests.</scope>
    <quality_bar>No breaking API changes. No broad exception swallowing.</quality_bar>
  </constraints>
  <verification>
    <required>Reproduce issue first.</required>
    <required>Add/adjust regression test.</required>
    <required>Run test suite for affected module and summarize results.</required>
  </verification>
  <output_format>
    <section name="root_cause">One paragraph.</section>
    <section name="changes">Exact files and what changed.</section>
    <section name="validation">Commands and outcomes.</section>
    <section name="risks">Residual risk and rollback option.</section>
  </output_format>
</prompt>
```

## 9) Implementation Notes for Skill Authors

<skill_integration_notes>
  <note>When the user provides model info, adapt style to that model family (GPT, reasoning, Codex).</note>
  <note>When the user omits constraints, infer minimum safe defaults and mark them as assumptions.</note>
  <note>Prefer XML-tagged sections for higher parsing reliability in downstream agents.</note>
  <note>Return one final improved prompt by default; optionally include a "compact" and "strict" variant.</note>
</skill_integration_notes>

## References

### Official OpenAI Docs
- OpenAI: Prompting. https://platform.openai.com/docs/guides/prompting
- OpenAI: Prompt Engineering. https://platform.openai.com/docs/guides/prompt-engineering
- OpenAI: Reasoning Best Practices. https://platform.openai.com/docs/guides/reasoning-best-practices
- OpenAI: Prompt Optimizer. https://platform.openai.com/docs/guides/prompt-optimizer/
- OpenAI: Code Generation (Codex Models). https://platform.openai.com/docs/guides/code-generation
- OpenAI: GPT-5.2 Model Guide. https://platform.openai.com/docs/guides/latest-model

### Codex Docs
- OpenAI Codex Docs: Prompting. https://developers.openai.com/codex/prompting/
- OpenAI Codex Docs: Overview. https://platform.openai.com/docs/codex/overview
- OpenAI Codex Docs: Agent Internet Access (prompt-injection context). https://platform.openai.com/docs/codex/agent-network

### OpenAI Cookbook
- OpenAI Cookbook: Codex Prompting Guide. https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- OpenAI Cookbook: GPT-5.2 Prompting Guide. https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide
- OpenAI Cookbook: GPT-5 Prompt Migration and Improvement Using the New Optimizer. https://cookbook.openai.com/examples/gpt-5/prompt-optimization-cookbook
- OpenAI Cookbook: Prompt Migration Guide. https://cookbook.openai.com/examples/prompt_migration_guide

### OpenAI Published Guidance
- OpenAI: How OpenAI uses Codex. https://openai.com/business/guides-and-resources/how-openai-uses-codex/
