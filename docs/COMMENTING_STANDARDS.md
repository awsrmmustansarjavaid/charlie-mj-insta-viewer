# Code Comments and Documentation Standards

## 1. Requirement

Every authored source-code file must contain a useful file-level purpose comment or equivalent module documentation. Comments should explain intent, boundaries, non-obvious decisions and important side effects.

Comments must not merely repeat the code line-by-line.

## 2. Language conventions

- TypeScript/JavaScript: `//` or `/** ... */`.
- Python: module docstring at the beginning of the file.
- Rust: `//!` module documentation and `///` for public APIs.
- HTML: `<!-- ... -->`.
- CSS: `/* ... */`.
- YAML: `#`.
- Shell scripts: `#`.
- SQL: `--` or `/* ... */`.
- Markdown: explanatory prose and headings.

## 3. JSON limitation

Strict JSON does not support comments. Do not insert `//` or `/* */` into `package.json`, lockfiles, `.webmanifest` or strict JSON configuration files because doing so makes them invalid.

For JSON files:
- Use descriptive property names.
- Explain configuration fields in a nearby Markdown document.
- Add a matching example or schema document when needed.
- Do not hand-edit generated lockfiles to add comments.

TypeScript configuration files may support JSONC comments depending on the tool, but keep the file valid for its parser.

## 4. What each source file should explain

At minimum:
- What the file is responsible for.
- What it exports or configures.
- Important dependencies or side effects.
- Whether it is demo-only, provider-backed or desktop-specific.
- Any security or data-integrity assumptions.

## 5. Function and API comments

Document public service functions with:
- Purpose.
- Input expectations.
- Return shape.
- Error conditions.
- Side effects.
- Permission or provider requirements.

## 6. Avoid misleading comments

Update comments when behavior changes. Never leave comments that claim a mock provider is live, that an approximate timestamp is exact, or that an unimplemented feature is complete.

## 7. Review checklist

- [ ] File-level purpose comment exists where the format permits it.
- [ ] Complex algorithms have intent comments.
- [ ] Public APIs document inputs, outputs and errors.
- [ ] Security-sensitive operations explain their constraints.
- [ ] Comments match actual behavior.
- [ ] JSON files remain valid strict JSON.
