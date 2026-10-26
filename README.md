# Theory of Everything Research Notes, October 2026

**Scalar-portal measurement bridges, an interferometry data audit and T-1 spectral matching**
MQGT-SCF / ZoraASI research program · Christopher Michael Baird · notes dated 10–12 October 2026

> **Status:** working notes (v0.1), not peer reviewed. Each note is an AI-assisted research calculation prepared for the author within the ZoraASI program, and each one states its own scope. They are conditional calculations and data audits. None of them reports a detection, claims new fundamental physics, or completes a Theory of Everything.

## The notes

| File | Date | Pages | What it does |
|---|---|---|---|
| `notes/Moving_Portal_Interferometry_Audit_2026-10-11.pdf` | 11 Oct | 6 | Reanalyses a public sodium-cluster interference dataset (95 fringe scans, 3,895 count observations) as a documented baseline. It also extends the scalar-portal calculation from a stationary point probe to moving, composite probes and mixed scalar species. It finds a mismatch between the code and the paper's optical cross-section that changes predicted visibility appreciably. No portal fit or exclusion is reported. |
| `notes/Quadratic_Portal_Measurement_Bridge_2026-10-11.pdf` | 11 Oct | 10 | Shows that a massive free scalar's quadratic operator has a nonzero thermal elastic-scattering contribution, which the symmetric Higgs portal couples to matter. Under a declared thermal state, a heavy fixed-path probe and a weak-coupling Markov approximation, this gives a calculable visibility-decay rate, extended to two mixed scalar modes. The scalar bath itself has not been measured. |
| `notes/T1_One_Loop_Spectral_Gauge_Matching_2026-10-12.pdf` | 12 Oct | 7 | Computes the one-loop contribution of a stated massive fermion spectrum to the hypercharge kinetic coefficient and quartic field response, in the four-copy sphere comparison model. A finite spectral remainder exists, but it does not fix a physical gauge coupling. |
| `notes/T1_Shared_Spectral_Action_Test_2026-10-12.pdf` | 12 Oct | 8 | Tests a stipulated common bosonic spectral action. It finds a conditional stationary radius, then shows that two spectral profiles with identical leading moments give different couplings, so the leading spectral data do not fix the gauge strength. |

## Supporting material

| Folder | Contents |
|---|---|
| `supporting/interferometry-audit-2026-10-11/` | Reanalysis and check scripts, results, figures and provenance for the first note. The third-party paper and dataset are not included (see below). |
| `supporting/quadratic-portal-2026-10-11/` | LaTeX source of the second note, its symbolic and numerical check script, saved checks and the rate-shape figure. |
| `supporting/t1-defect-notes-2026-10-10_11/` | Two earlier T-1 notes, kept as their original archives: a wrapped-defect charge and zero-mode audit (10 Oct) and a global anomaly and source follow-up (11 Oct). Each has its own research note, verification script, provenance and checksums. |
| `CHECKSUMS.sha256` | SHA-256 of every file in this repository. |

### Reproducing the checks

The scripts need Python 3 with `sympy`, `mpmath`, `numpy`, `scipy` and `matplotlib`. The originals were run with Python 3.13.5 and sympy 1.14.0.

- `supporting/quadratic-portal-2026-10-11/check_quadratic_bridge.py` re-derives and checks the quadratic-portal results.
- `supporting/interferometry-audit-2026-10-11/check_moving_kernel.py` checks the static and moving-probe kernels.
- `reproduce_baseline.py` and `check_optical_inputs.py` in the same folder need the public sodium-cluster data. Download `Na-Cluster-Interference.zip` from [Zenodo record 17502163](https://zenodo.org/records/17502163) (CC BY 4.0), which accompanies [doi:10.1038/s41586-025-09917-9](https://doi.org/10.1038/s41586-025-09917-9). Unpack it so that `author_source/Na-Cluster-Interference/` sits next to the scripts. `source_integrity.json` lists the expected SHA-256 of every original file.
- Each T-1 archive contains a `README.md` with its own run command.

These are deterministic calculation checks, not experimental significance tests.

## Relationship to other work

- Part of the MQGT-SCF / Theory of Everything program, whose versioned corpus is on Zenodo under concept DOI [10.5281/zenodo.14019809](https://doi.org/10.5281/zenodo.14019809). These four notes are not included in the corpus edition of 22 October 2026.
- The T-1 notes use the four-copy odd-lattice sphere model as an illustrative comparison branch, not as part of the original toroidal MQGT-SCF action.

## AI assistance and provenance

Christopher Michael Baird leads the research program. The two notes dated 11 October describe themselves as AI-assisted research calculations prepared for the ZoraASI project. The two T-1 notes dated 12 October state that they were prepared with ChatGPT, and the supporting T-1 archives come from the same AI-assisted workflow. Claude (Anthropic) assembled this repository and its metadata; no note was changed. Some provenance records (`manifest.json`, `research_state.json`) contain absolute file paths from the author's computer. They are kept unchanged so the recorded checksums still verify.

## Citation

See `CITATION.cff`. Each GitHub release of this repository is archived on Zenodo with a DOI.

## License

The notes, figures and data are licensed CC BY 4.0, and the code MIT; see `LICENSE.md`. Third-party papers and datasets are cited, not included, and remain under their own terms.
