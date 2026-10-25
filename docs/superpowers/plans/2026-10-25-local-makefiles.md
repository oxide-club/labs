# Local Makefiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Deliver the approved independent Make interface and reproducible VM environments.

**Architecture:** Local Makefiles delegate existing builds and local Python helpers. Canonical templates and declarative preparation data generate checked-in independent copies. QEMU environments use a verified Alpine ISO and APKs, a diskless disposable root, a nonprivileged guest account and explicit guest confirmation.

**Tech Stack:** GNU Make, Python 3.10+, existing C/Rust/Go toolchains, QEMU, libarchive bsdtar.

**Spec:** `docs/superpowers/specs/2026-10-25-local-makefiles-design.md`

## Global Constraints

- Default action is help; preserve starter failures, fixtures and published paths.
- No global package installation, no parent-directory dependency in downloaded labs.
- VARIANT=reference is default; MODE=gpu is the GPU default.
- clean preserves evidence and user files; VM execution never confirms on the host.
- Keep build/ and results/ out of distributed packages.

## Review Focus

- Package relocated outside the repository must still run (Task 2).
- Invalid selectors and missing tools must fail before executing anything (Task 1).
- clean must reject symlink paths and preserve evidence and foreign files (Task 1).
- Environment setup must reject checksum mismatches and never execute host starters (Task 3).
- VM failures and missing guest confirmation must not become successful checks (Task 3).

### Task 1: Local interface and pilot labs

**Files:** `templates/make/lab.py`, `scripts/prepare-make.py`, `docs/make-labs.json`, `tests/test_make.py`; generated `Makefile`, `materials/lab.py`, `materials/lab.json` in each pilot.
**Interfaces:** `VARIANT=NAME MODE=NAME python3 materials/lab.py ACTION`; JSON action argv lists, tool requirements, known generated files. Generator `--check` verifies local copies.

- [x] Add behavioral tests for help, unknown selectors, build/test distinction, missing tools and conservative clean in temporary package copies; run and observe failures.
- [x] Implement local dispatcher with bounded subprocess execution, existing Make delegation, argv execution without shell interpolation and selected preparation checks.
- [x] Generate pilots 007, 003, 016; test setup/build and refusal of dynamic VM-only commands without an environment.
- [x] Run `python3 -m unittest discover -s tests`; commit the interface.

### Task 2: All labs and distribution

**Files:** `docs/make-labs.json`, all local Makefiles/helpers, README files, `templates/README.md`, `CONTRIBUTING.md`, `scripts/validate.py`, `tests/test_make.py`, sibling website `src/lib/lab-files.mjs`, `tests/lab-files.test.mjs`.
**Interfaces:** Same local dispatcher and generated manifests; variant preparation data from existing manifests.

- [x] Add failing tests for all 18 interfaces, isolated distributed copies, variant selection and root Makefile inclusion.
- [x] Map existing reference builds/checks/experiments and maintained variants; provide compile-only steps when checks currently build internally.
- [x] Update local and website distribution allowlists with exact names; exclude generated evidence/environment state.
- [x] Run interface tests, full Python suite, generator check, structural validation and website distribution tests; commit.

### Task 3: Disposable environments

**Files:** `templates/make/environment.py`, `templates/make/environment.json`, `tests/test_environment.py`, generated copies in 002/003/016, local environment docs.
**Interfaces:** `python3 materials/environment.py setup|shell|clean|exec [ACTION]`; generated Make env-* targets. env exec transfers only distributed source and writes exported evidence under results/.

- [x] Add failing tests for download digest verification, guest argv, unconfirmed execution, source selection, network-off execution and cleanup containment.
- [x] Verify official image/toolchain sources; pin immutable image checksums and installed package inputs. Implement QEMU disposable sessions, bounded boot/commands, nonprivileged execution and guest confirmation.
- [x] Integrate dynamic test/run/verify-preparation dispatch for 002/003/016; preserve manual VM path and existing 016 guards.
- [x] Exercise real boot/setup, ASan/LSan, 016 guard and evidence export; report exact infrastructure limitations if unavailable.
- [x] Run tests and generator check; commit.

### Task 4: Final verification and review

**Files:** documentation and fixes identified during validation.
**Interfaces:** Existing editorial verification and local Make commands.

- [x] Run full Python suite, cache model, report check, validate, selected preparation and variant checks. Distinguish expected starter failures from environment errors.
- [x] Run fresh-context whole-branch review; fix material findings with regression tests.
- [x] Document tested configurations and limitations, update this checklist, commit and leave the branch ready for review without publishing.

Continuation: validated all remaining labs in 19 configurations (133 commands),
documented local experiments/selectors, and fixed GPU setup to check resources
using the existing non-starter CUDA probe. See `docs/make-validation.md`.
