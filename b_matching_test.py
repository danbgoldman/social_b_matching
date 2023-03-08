# Copyright 2022 The social_b_matching Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for b-matching."""

from absl.testing import absltest
from absl.testing import parameterized

from social_b_matching import b_matching


class BMatchingTest(absltest.TestCase):
  """Unit Tests for b-matching."""

  # With three nodes, only one pair can be matched.
  def testThreeNodesB1(self):
    b_maxs = [1, 1, 1]
    weights = {(0, 1): 1, (1, 2): 1, (2, 0): 1}

    result = b_matching.maximize_weighted_b_matching(b_maxs, weights)
    self.assertLen(result, 1)
    self.assertContainsSubset(result, [(0, 1), (1, 2), (2, 0)])

    with self.assertRaises(b_matching.SolverError,
                           msg='The solver could not solve the problem.'):
      b_matching.maximize_weighted_b_matching(b_maxs, weights, b_min=1)

    result = b_matching.inclusive_matching(b_maxs, weights)
    self.assertLen(result, 1)
    self.assertContainsSubset(result, [(0, 1), (1, 2), (2, 0)])

  def testThreeNodesB2(self):
    result = b_matching.maximize_weighted_b_matching([2, 2, 2], {
        (0, 1): 1,
        (1, 2): 1,
        (2, 0): 1
    })
    self.assertListEqual([(0, 1), (1, 2), (2, 0)], result)

  def testFourNodesB1(self):
    result = b_matching.maximize_weighted_b_matching([1, 1, 1, 1], {
        (0, 1): 1,
        (0, 2): 1,
        (0, 3): 1,
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): 1
    })
    self.assertLen(result, 2)
    self.assertContainsSubset(result, [(0, 1), (0, 2), (0, 3), (1, 2),
                                       (1, 3), (2, 3)])

  def testFourNodesB2(self):
    result = b_matching.maximize_weighted_b_matching([2, 2, 2, 2], {
        (0, 1): 1,
        (0, 2): 1,
        (0, 3): 1,
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): 1
    })
    self.assertLen(result, 4)
    self.assertContainsSubset(result, [(0, 1), (0, 2), (0, 3), (1, 2),
                                       (1, 3), (2, 3)])

  def testFourNodesB3(self):
    result = b_matching.maximize_weighted_b_matching([3, 3, 3, 3], {
        (0, 1): 1,
        (0, 2): 1,
        (0, 3): 1,
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): 1
    })
    self.assertListEqual(result, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3),
                                  (2, 3)])

  # This case shows how one node (3) can be left out of the maximum b-matching.
  def testFourNodesB1B2(self):
    b_maxs = [2, 1, 1, 1]
    weights = {
        (0, 1): 3,
        (0, 2): 2,
        (0, 3): 1,
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): 1,
    }
    result = b_matching.maximize_weighted_b_matching(b_maxs, weights)
    self.assertListEqual(result, [(0, 1), (0, 2)])

    result = b_matching.maximize_weighted_b_matching(b_maxs, weights, b_min=1)
    self.assertListEqual(result, [(0, 1), (2, 3)])

    result = b_matching.inclusive_matching(b_maxs, weights)
    self.assertListEqual(result, [(0, 1), (2, 3)])

  # Test input validation
  def testBadBMax(self):
    with self.assertRaises(ValueError):
      b_matching.maximize_weighted_b_matching([1, 2, 3, 0], {})

    with self.assertRaises(ValueError):
      b_matching.maximize_weighted_b_matching([1, -2, 3, 1], {})

  def testBadEdges(self):
    with self.assertRaises(ValueError):
      b_matching.maximize_weighted_b_matching([1, 1, 1], {
          (0, 1): 1,
          (-1, 2): 1,
          (2, 0): 1
      })

    with self.assertRaises(ValueError):
      b_matching.maximize_weighted_b_matching([1, 1, 1], {
          (0, 1): 1,
          (1, 3): 1,
          (2, 0): 1
      })

  def testSelfEdges(self):
    # Self-edges are only invalid for inclusive matching.
    with self.assertRaises(ValueError):
      b_matching.inclusive_matching([1, 1], {
          (0, 1): 1,
          (1, 1): 1
      })

  def testDupEdges(self):
    # Duplicate edges are only invalid for inclusive matching.
    with self.assertRaises(ValueError):
      b_matching.inclusive_matching([1, 1, 1], {
          (0, 1): 1,
          (1, 0): 1,
          (1, 2): 1,
      })

  def testBadWeight(self):
    with self.assertRaises(ValueError):
      b_matching.maximize_weighted_b_matching([1, 1, 1], {
          (0, 1): 1,
          (1, 2): -0.5,
          (2, 0): 1
      })


class CheckInclusiveTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(testcase_name='good_one_edge',
           b_maxs=[1, 1, 1], edges=[(0, 1)],
           success=True, not_max=[2]),
      dict(testcase_name='good_two_edges',
           b_maxs=[1, 2, 1], edges=[(0, 1), (1, 2)],
           success=True, not_max=[]),
      dict(testcase_name='bad_extra_edge',
           b_maxs=[1, 1, 1], edges=[(0, 1), (1, 2)],
           success=False, not_max=[1]),
      dict(testcase_name='bad_missing_edge',
           b_maxs=[1, 2, 1], edges=[(0, 1)],
           success=False, not_max=[1, 2]))
  def testCheckInclusive(self, b_maxs, edges, success, not_max):
    result = b_matching.check_inclusive(b_maxs, edges)
    self.assertTupleEqual(result, (success, not_max))

  @parameterized.named_parameters(
      dict(testcase_name='high',
           b_maxs=[1, 1, 1], edges=[(0, 1), (1, 2), (2, 3)]),
      dict(testcase_name='low',
           b_maxs=[1, 1, 1], edges=[(0, -1), (1, 2)]))
  def testCheckInclusiveBadInput(self, b_maxs, edges):
    with self.assertRaises(ValueError):
      b_matching.check_inclusive(b_maxs, edges)


if __name__ == '__main__':
  absltest.main()
