# packages/contracts: LOCKED

These schemas are the boundary between Sanket's and Sahil's services. Treat any change here as an API change.

A change to this package must, in the same PR:
1. Update `docs/specs/<spec>/SPEC.md` to describe the change.
2. Bump `CONTRACT_VERSION` in `src/bolchaal_contracts/version.py`. Use minor for additive changes and major for breaking ones.
3. Re-export the schemas with `uv run python -m bolchaal_contracts.export` and commit `schemas/*.json`.
4. Add or adjust tests in `tests/`.
5. Get approval from **both** founders.

Models only. No I/O, no business logic, and no dependencies beyond pydantic.
