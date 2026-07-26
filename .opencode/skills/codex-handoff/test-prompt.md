Goal:
  Produce an actionable implementation roadmap for adding a dark mode toggle
  to the existing settings page in example-todo-app.

Current state (Point A):
  - Single-page todo app. Settings at /src/settings/Settings.jsx.
  - Settings has: display name editor, email notification toggle, Delete Account button.
  - CSS Modules, light-mode only. No theme mechanism.
  - No localStorage theme key.

Desired state (Point B):
  A dark mode toggle at the top of settings. Persists to localStorage key "example-todo:theme".
  Initial default from prefers-color-scheme. CSS-only dark overrides in Settings.module.css.

Constraints:
  - React 18, plain .jsx. CSS Modules only. No new deps.
  - Must be implementable in <= 2 hours by one developer.

Non-goals:
  - No full-app theme system. No other pages. No state management lib.

Relevant context:
  - Settings.jsx: functional component, ~80 lines, useState for form state.
    Imports ./Settings.module.css. Renders h1, section with fields.
  - Settings.module.css: ~60 rules, all light-mode. Classes: .container,
    .heading, .section, .field, .label, .input, .checkbox, .dangerButton.
  - index.css: global reset + font stack. No theme variables.

Specific questions:
  1. Exact file change list in order?
  2. CSS custom properties in index.css (global) or Settings.module.css?
  3. Toggle init: localStorage + matchMedia fallback?
  4. Minimal CSS variable overrides for dark settings (light→dark values)?
  5. Delete Account button color in dark mode?
  6. Accessibility: label, aria, contrast ratios?
  7. Should toggle follow OS preference changes after manual override?
  8. Edge cases to test manually?

Output format: Markdown roadmap with summary, steps, testing, risks, effort estimate.
