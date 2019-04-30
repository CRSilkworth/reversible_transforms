import unittest
import reversible_transforms.utils.test_helpers as th
import reversible_transforms.tanks.mean as me
import numpy as np


class TestMean(th.TestTank):

  def test_one_d(self):
    self.pour_pump(
      me.mean,
      {'a': np.array([1, 3]), 'axis':()},
      {'target': np.array(2), 'a': np.array([1, 3]), 'axis': None},
      type_dict={'a': np.ndarray, 'axis': int}
    )

  def test_two_d(self):
    self.pour_pump(
      me.mean,
      {'a': np.array([[0, 1], [2, 3], [4, 5], [1, 0]]), 'axis': 1},
      {
        'target': np.array([0.5, 2.5, 4.5, 0.5]),
        'a': np.array([[0, 1], [2, 3], [4, 5], [1, 0]]),
        'axis': 1
      },
      type_dict={'a': np.ndarray, 'axis': int}
    )

    self.pour_pump(
      me.mean,
      {'a': np.array([[0, 1], [2, 3], [4, 5], [1, 0]]), 'axis': 0},
      {
        'target': np.array([1.75, 2.25]),
        'a': np.array([[0, 1], [2, 3], [4, 5], [1, 0]]),
        'axis': 0
      },
      type_dict={'a': np.ndarray, 'axis': int}
    )

  def test_three_d(self):
    self.pour_pump(
      me.mean,
      {'a': np.arange(24).reshape((2, 3, 4)), 'axis': (0, 1)},
      {
        'target': np.array([10, 11, 12, 13]),
        'a': np.arange(24).reshape((2, 3, 4)),
        'axis': (0, 1)
      },
      type_dict={'a': np.ndarray, 'axis': int}
    )

if __name__ == "__main__":
    unittest.main()