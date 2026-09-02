# Repair checklist

Process: `repair.v1`
Issue: `#18`
Correlation ID: `31812202249`

- [x] Reproduce the original failure
- [x] Fix the root cause
- [x] Add or update regression tests
- [x] Update implementation documentation
- [x] Produce digest-bound ticket2dsl, code2dsl, docs2dsl and service2dsl projections
- [x] Complete every Repair TODO item
- [ ] technical check failed: test
- [ ] make test (doctor-test) fails: 5 tests in tests/test_runtime.py raise ModuleNotFoundError: No module named 'PIL'. Either add Pillow (llm-vision extra) to install-dev/dev dependencies or make the test fixture skip when Pillow is unavailable.
- [ ] LLM verdict: REQUEST_CHANGES
