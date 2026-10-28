# UGT route-replacement as a template for MQGT-SCF errata handling

**Date:** 27 October 2026  
**Spirit match:** open-by-design stance on E4 (T-1 α⁻¹ gate) in `Cbaird26/mqgt-scf-continued`  
**Source studied:** Axiom Math, *The Unbalanced Group Theorem* (`media/ugt.pdf`)

## What Axiom did when a literature route broke

1. **Localize the failure.** They did not declare UGT false. They found counterexamples to a *closure assertion* inside Walter’s 1986 memoir route (field involutions; e.g. PSL₂(49) → component PSL₂(7) outside the chosen family L₀).
2. **Keep the target claim explicit.** The simple-group UGT statement stayed the goal; the broken *argument* was retired.
3. **Prefer a documented alternate route** over silent patching — Solomon (1976) maximal 2-components; new preservation theorem stated with hypotheses.
4. **Record other valid routes** (Harris / Gorenstein; GLS odd-type) so readers know the obstruction is route-specific.
5. **Publish the obstruction and the repair** as first-class research objects (paper + Lean), not buried commit messages.
6. **Separate marketing scale from citable inventory** when counting mistakes.

## Mapping onto MQGT-SCF / E4 practice

| Axiom UGT move | MQGT-SCF analogue already in use |
|---|---|
| Counterexample to a step, not to the whole theorem | E4: residual vs CODATA is real; fitted “fixes” are uncertifiable (58 gate-passing coincidences) — structural derivation required |
| Do not claim the end goal is dead | E4 remains open by design; T-1 identity stands as a six/seven-digit approximation, not an eight-digit derivation |
| New theorem / route with explicit hypotheses | Sequestering note, middle-tower lemmas, Door 1/2 exclusions — positive or negative results with certificates |
| Errata list + frozen verification | `ERRATA_STATUS.md`, `LEDGER.md`, `mqgt-scf-independent-verification` v1.0-paper |
| Lean kernel check of stated theorems | E13 Lean kernels (forcing chain), with explicit scope limits (not spectral numerics as physics evidence) |

## Template checklist for the next literature break in this estate

When a published or corpus-internal argument fails under re-derivation:

1. Write the **failed step** and a **minimal counterexample or numerical exclusion** (as with Door 1/2 and the Walter closure failure).
2. State whether the **parent claim** is (a) still believed under other routes, (b) weakened, or (c) retired.
3. If replacing the route, state **hypotheses of the new argument** and what it does *not* prove.
4. Land the disposition in `ERRATA_STATUS.md` / `LEDGER.md` (or a dated research_continuation note), never only in chat.
5. If Lean/machine-check is used, label the **scope** (what the kernel actually covers).
6. Never upgrade a formal-verification landscape win (e.g. CFSG Lean) into a physics confirmation.

## One-line policy

**Broken routes get replaced or marked open; they do not get laundered into stronger claims.**
