# Assurance Case Template (GSN-lite)

> Every case under `docs/PhaseC/cases/` MUST contain every section below
> with a non-empty body. The `assurance_lint.py` tool enforces this.

```
G : Goal (claim)
S : Strategy (how the goal decomposes)
G.x : Sub-goal
Sn : Solution / Evidence
C : Context
A : Assumption
J : Justification
```

## Required sections (in this exact order)

### 1. Identity
```
model_name:    <string>
version:       <semver>
case_owner:    <name or role>
last_reviewed: <ISO date>
state:         auto-generated | reviewer-confirmed | board-approved
```

### 2. Top claim (G1)
> A single sentence claim about safety in operational context.
> Example: *"The fault_escape_predictor is safe to use as an advisory
> input to the verification team's prioritization workflow."*

### 3. Context (C1..Cn)
- Operational environment
- Upstream / downstream systems
- DAL / IDAL assumption (if any)
- Data sources
- User population

### 4. Assumptions (A1..An)
- Each assumption is **falsifiable**
- If any assumption fails, the case must be re-reviewed

### 5. Strategy (S1)
> How the top claim is decomposed into sub-goals (typically 3–6).

### 6. Sub-goals + evidence (G1.1, G1.2, ..., each with Sn)
For each sub-goal:
- statement
- list of evidence pointers (`Sn1`, `Sn2`, ...) — each must be a real
  artifact path, registry entry, or test id

### 7. Failure modes
- known limitations
- worst-case behavior
- which sub-goal each failure mode invalidates

### 8. Fallback behavior
- What happens when the model is wrong / unavailable
- Pointer to the deterministic counterpart that always runs

### 9. Human override path
- Who can override the model output
- How is the override recorded

### 10. Change impact
- Which dataset_hash / git_sha values invalidate this case
- Required re-review trigger

### 11. Standards mapping
- DO-178C objective table cells touched
- ARP4754A allocation
- ARP4761A failure conditions referenced
- DO-330 tool qualification linkage

### 12. Reviewer log
| Reviewer | Role | Date | State after | Notes |
|---|---|---|---|---|
