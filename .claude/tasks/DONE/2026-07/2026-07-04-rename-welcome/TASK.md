# TASK — 2026-07-04-rename-welcome
owner: Engineer
immutable: true

## Requirements
- R1: Rename the home heading text "Hello World" to "Welcome" in frontend/app/page.tsx.
- R2: Update the coupled test frontend/__tests__/page.test.tsx so its heading
      assertion (and describe/it labels) match "Welcome" — the rename is the direct
      cause of the test change, so they move together.

## Acceptance
- A1: page.tsx <h1> renders "Welcome".
- A2: page.test.tsx asserts the "Welcome" heading and passes.
- A3: Only the heading text + its test change; no markup, class, import, or logic change.

## Constraints
- Text-only change to the heading and its matching test.
