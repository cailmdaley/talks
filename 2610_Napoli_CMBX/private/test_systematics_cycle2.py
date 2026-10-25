"""Cheap regression checks for the Cycle-2 triangle's input/error contract.

Run with the container's Python (no products written):
  app python -m unittest discover -s docs/talks/2610_Napoli_CMBX/private -p 'test_systematics_cycle2.py'
The real-archive route additionally checks window hashes, CSV crosses, grids,
and the science covariance order and diagonal against each saved pair block.
"""
import unittest

import numpy as np

from make_systematics import template_auto, xell


class Cycle2Contract(unittest.TestCase):
    def rows(self, column, value):
        return [dict(ell=str(ell), **{column: str(value)})
                for _ in range(12) for ell in (112., 140.5)]

    def test_generic_column_is_this_templates_auto(self):
        # The current writer uses the same column name in every archive.
        np.testing.assert_array_equal(
            template_auto(self.rows('c_extinction_extinction', 7), 'noise_vis', [112., 140.5]), [7, 7])
        np.testing.assert_array_equal(
            template_auto(self.rows('c_extinction_extinction', 3), 'extinction_vis', [112., 140.5]), [3, 3])

    def test_named_column_takes_precedence(self):
        rows = self.rows('c_psf_psf', 7)
        for row in rows:
            row['c_extinction_extinction'] = '3'
        np.testing.assert_array_equal(template_auto(rows, 'psf_vis', [112., 140.5]), [7, 7])

    def test_repeated_auto_and_grid_must_match(self):
        for column in ['ell', 'c_extinction_extinction']:
            with self.subTest(column=column):
                rows = self.rows('c_extinction_extinction', 7)
                rows[-1][column] = '8'
                with self.assertRaises(AssertionError):
                    template_auto(rows, 'noise_vis', [112., 140.5])

    def test_tiny_auto_mismatch_is_not_hidden_by_absolute_tolerance(self):
        rows = self.rows('c_extinction_extinction', 1e-43)
        rows[-1]['c_extinction_extinction'] = '2e-43'
        with self.assertRaises(AssertionError):
            template_auto(rows, 'zodiacal_vis', [112., 140.5])

    def test_fixed_auto_gaussian_propagation(self):
        c = {'a': (np.array([2.]), np.array([.1]), None),
             'b': (np.array([3.]), np.array([.2]), None)}
        x, sx = xell(c, {'cl': [4.]}, 'a', 'b')
        np.testing.assert_allclose(x, [1.5])
        np.testing.assert_allclose(sx, [np.hypot(.075, .1)])
        x, sx = xell(c, {'cl': [4.]}, 'a', 'a')
        np.testing.assert_allclose(x, [1.])
        np.testing.assert_allclose(sx, [.1])


if __name__ == '__main__':
    unittest.main()
