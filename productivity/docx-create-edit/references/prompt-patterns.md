# Prompt Patterns

Use these patterns to gather just enough information before creating or editing the document.

## Create From Scratch

Collect:
- document purpose
- recipient or organization
- applicant name and role
- required sections or fields
- tone and length
- output filename

Prompt shape:

```text
Create a DOCX application form for [role or program].
Applicant: [name]
Recipient: [organization]
Required sections: [list]
Tone: [formal / concise / persuasive]
Include a supporting statement with concrete examples.
Save as [filename].
```

## Edit Existing Form

Collect:
- source `.docx` path
- insertion anchor or section name
- rough idea to add
- facts that must stay unchanged
- output filename

Prompt shape:

```text
Read this application form DOCX: [path]
Add or update the section [section name].
Add this idea: [rough text or requirement]
Preserve the existing structure and official wording.
Save the result as [filename].
```

## Rewrite Rough User Text

When the user gives short or broken wording, normalize it before insertion.

Example:

```text
User idea:
"I am computer engineer so that i can do this with examples and supportive ideas."

Rewrite target:
"I am a computer engineer with training in structured problem solving, software systems, and technical analysis. I can apply those skills directly to this role by breaking down complex requirements, proposing practical solutions, and supporting recommendations with concrete examples from my work or studies. This combination of technical depth and clear communication helps me contribute effectively in both execution and planning."
```

Treat the rewritten paragraph as a draft. Remove claims that are not supported by user facts.
