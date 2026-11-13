import numpy as np
import pytest
from sklearn.metrics import r2_score

from src.modele import r2_numpy


def test_r2_numpy_egal_sklearn():
    rng = np.random.default_rng(0)
    y = rng.random((50, 4))
    p = y + rng.normal(0, 0.1, (50, 4))
    assert r2_numpy(y, p) == pytest.approx(r2_score(y, p))