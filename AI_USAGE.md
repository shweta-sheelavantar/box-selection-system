# AI Usage Log

This document records how AI tools were used during the development of this project,
as required by the assignment guidelines. All sections must be completed in your own words.

---

## Tools Used

- **Kiro (AI coding assistant)** — used throughout the development session for code generation,
  debugging, and explanation of Django concepts.

---

## Prompts

The table below summarises the key prompts from the session (paraphrased — see the
attached chat transcript for the exact wording):

| # | Prompt summary | Purpose |
|---|---|---|
| 1 | "Explain the existing project structure and identify what to implement next" | Understanding starting point |
| 2 | "yes start" → build data models for Box, Product, Order, OrderItem | Step 1 implementation |
| 3 | "ok" → write the box selection algorithm in services.py | Core business logic |
| 4 | "yes" → build views, forms, and URLs for the order flow | Web layer |
| 5 | "yes" → build the HTML templates with Bootstrap 5 | UI |
| 6 | "yes" → write a full Django TestCase test suite | Testing |
| 7 | Full spec prompt: redesign for multi-product orders, add Order model, cheapest-box logic | Major redesign after reading the full assignment |
| 8 | "yes" → rebuild templates for the new Order-based flow | UI rebuild |
| 9 | "yes" → write 29 tests with Django TestCase | Testing |
| 10 | "run and give link to use, frontend" | Start dev server | 
| 11 | Detailed spec: add seed_data command, update forms/views/template for empty-state warning | Data seeding and UX |
| 12 | "Create README, requirements.txt, CI workflow, AI_USAGE, .gitignore" | Project documentation |

---

## Accepted Output

Describe which AI-generated code or explanations you accepted with little or no change.
Examples:

- The `models.py` field definitions (DecimalField, ForeignKey, ManyToManyField through OrderItem)
- The `services.py` algorithm structure — weight check then packing check, cheapest-first loop
- The Bootstrap 5 template layout and card structure
- The management command `seed_data.py` using `get_or_create`
- The GitHub Actions workflow YAML

---

## Rejected or Modified Output

Describe any AI output you changed, rejected, or decided not to use, and explain why.
Examples:

- *(Add your own observations here)*
- *(Did any generated code not match your project's style?)*
- *(Did you simplify or rewrite any section?)*

---

## Mistakes the AI Made

TODO: write in my own words

*(Describe any errors, bugs, or incorrect assumptions the AI made during the session.
For example: wrong model field names, stale imports after a redesign, incorrect test assertions, etc.)*

---

## How I Verified

TODO: write in my own words

*(Describe how you checked that the AI-generated code was correct.
For example: running the test suite, manually testing the form in the browser,
reading through the generated algorithm and tracing it with the sample data, etc.)*
