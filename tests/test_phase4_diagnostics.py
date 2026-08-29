import numpy as np

from diagnostics_gp import _rhat


def test_rhat_reports_constant_chains_as_one():
    chains = [
        np.ones((20, 3)),
        np.ones((20, 3)),
        np.ones((20, 3)),
    ]

    np.testing.assert_array_equal(_rhat(chains), np.ones(3))
