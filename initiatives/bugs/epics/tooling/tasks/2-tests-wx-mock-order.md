## 2. test_myimport mocks wx by import order

- **Status:** Open
- **Symptom:** `tests/test_myimport.py` swaps `sys.modules["wx"]` for a `Mock` at import time; modules already imported keep the real `wx`.
- **Where:** `tests/test_myimport.py`; `TRELBY_TESTING` (`trelby/config.py:14-19`) is never set
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** results depend on test order.
