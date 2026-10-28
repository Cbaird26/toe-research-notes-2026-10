# Axiom CFSG formal-verification landscape note

**Date:** 27 October 2026 (America/New_York)  
**Status:** working note, not peer reviewed. Landscape citation only.  
**Does not claim:** that Axiom’s CFSG formalization supports, validates, or proves MQGT-SCF / ToE physics claims.

## Purpose

Record the public formal-verification landscape around Axiom Math’s Lean formalization of the Classification of Finite Simple Groups (CFSG), and fix how that work relates (and does not relate) to the MQGT-SCF / ToE research estate under `Cbaird26`.

## Primary citations

1. Axiom blog — *Formalizing the Enormous Theorem*  
   https://axiommath.ai/research/the-enormous-theorem-formalized/
2. Interactive site / proof map / errata surface  
   https://cfsg.axiommath.ai/
3. Lean repository  
   https://github.com/AxiomMath/CFSG
4. Unbalanced Group Theorem paper (Axiom Math; hexagonmath preprint `2610.00575v1`)  
   Local copy: `media/ugt.pdf` (text extract: `media/ugt.txt`)  
   Source fetch: https://hexagonmath.org/pdf/2610.00575v1

## What Axiom announced (compressed)

- Complete Lean formalization of CFSG following the first-generation proof (~43.1M lines; ~715 papers/books in the corpus map).
- Written record: most literature issues found were minor; **34 noteworthy deviations**; the most substantial concerned a published route to the **Unbalanced Group Theorem (UGT)**.
- Video / press scale numbers (thousands of errata) are larger than the written “34 noteworthy” count; treat the blog + UGT paper as the citable record until a full public errata database is released.
- Repair for the Walter (1986) UGT route: Solomon (1976) maximal 2-components; new **Preservation of simple tops** (Theorem 2.3 in the UGT paper). Separate named example: Aschbacher–Smith quasithin numerical equality failure for SL₂(5).

## Relation to this research program

| Link type | Assessment |
|---|---|
| Methodological | **Strong analogy.** Same culture as `mqgt-scf-continued` errata E1–E13, LEDGER, Lean kernels (E13), frozen verification snapshots. |
| Shared math objects | **Weak / thematic.** CFSG classifies *finite* simple groups (symmetry atoms). MQGT-SCF uses continuous gauge / spectral-action / scalar-portal structure. No CFSG theorem is a load-bearing axiom of Part 0. |
| Physics bridge via Monster / moonshine | **Soft citation only** (Axiom blog). Not used to underwrite MQGT-SCF claims. |
| Nearest group-adjacent neighbors in this estate | `zoraasi-fulldash-reports-2026` Band-1 probes: Andrews–Curtis and Farrell–Jones (see `GROUP_THEORY_NEIGHBORS.md`). Finite computational probes; **no proofs claimed**. |

## Explicit non-claims

- Do **not** cite CFSG Lean as evidence that MQGT-SCF / ToE is true.
- Do **not** open GitHub issues asserting “ToE supported by CFSG / Axiom.”
- Do **not** treat video marketing counts as the errata inventory.

## Companion notes in this folder

- `UGT_ROUTE_REPLACEMENT_TEMPLATE.md` — how the UGT repair maps onto E4-style honest errata handling.
- `STANDING_AXIOM_ERRATA_WATCH.md` — future scan when Axiom’s full errata DB appears.
- `GROUP_THEORY_NEIGHBORS.md` — cross-links to fulldash Andrews–Curtis / Farrell–Jones.
- `media/` — saved UGT PDF/text, Axiom announcement stills, and the announcement video.

## Provenance

Prepared 2026-10-27 for Christopher Michael Baird within the ZoraASI / Grok Bot research workflow after reviewing the public Axiom announcement thread, blog, UGT paper, `AxiomMath/CFSG`, and public `Cbaird26` ToE repos. Media files were downloaded from X / hexagonmath on that date.
