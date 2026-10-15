# mpr-gamma-surge
Plan: `docs/plan.md` (binding). Read only the section for the current milestone.
## Rules
- Work one milestone at a time (MS0–MS15, Table 11.1). Stop at each gate and report.
- Python 3.11 in .venv, CPU only. Do not use PyDSTool.
  Install from environment/requirements-lock.txt.
- Plain `python` is NOT the venv (it resolves to 3.12). Always use `.venv\Scripts\python.exe`.
- Run `.venv\Scripts\python.exe -m pytest -m "not slow"` before every commit.
  Run the full suite before every tag.
- Drivers only integrate, analysis modules only analyse, figure scripts
  only plot (section 10.1).
- Never edit results/ or figures/ by hand; they are git-ignored outputs.
- Never invent an equation, value or citation. Where the plan says UNVERIFIED
  or [needs decision], use its default and say so; do not fill gaps from memory.
- Every run writes a provenance record (section 6.6). Every change of a
  default gets a docs/decision_log.md entry (Appendix C).
- Commit format: <type>(<scope>): <summary> [IDs]. Do not push or tag unless asked.
## Layout
src/mprsurge/ code; tests/ tests; configs/ YAML; scripts/ drivers and figures;
docs/ notes (section 10.1).
