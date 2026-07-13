import os
import sys

import pandas as pd
import pytest

# Ensure the repo root is importable (so ``import utils`` / ``DataCuration`` work
# regardless of where pytest is invoked from).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DB_XLSX = os.path.join(REPO_ROOT, "Assets", "20260418_cNPDB.xlsx")
DB_PARQUET = os.path.join(REPO_ROOT, "Assets", "20260418_cNPDB.parquet")


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def db():
    """The shipping cNPDB database (xlsx)."""
    if not os.path.exists(DB_XLSX):
        pytest.skip(f"database not found at {DB_XLSX}")
    return pd.read_excel(DB_XLSX)


@pytest.fixture(scope="session")
def db_parquet():
    if not os.path.exists(DB_PARQUET):
        pytest.skip(f"parquet not found at {DB_PARQUET}")
    return pd.read_parquet(DB_PARQUET)
