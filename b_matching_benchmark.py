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

"""Speed tests for bmatching."""

import random
import timeit

from typing import Sequence

from absl import app

from social_b_matching import b_matching

BMAX_1_RATIO = .7  # 70 percent of nodes have b_max == 1
BMAX_2_RATIO = .1  # 10 percent of nodes have b_max == 2
BMAX_3_RATIO = .2  # 20 percent of nodes have b_max == 3


def solve_and_print_count(b_maxs, weights):
  edges = b_matching.maximize_weighted_b_matching(
      b_maxs, weights, timeout_ms=2000)
  print('Selected', len(edges), 'edges for', len(b_maxs), 'nodes')


def b_matching_benchmark(n):
  """Tests performance of b-matching on a fully connected graph of n nodes."""

  # Determine number of nodes with each b_max
  nb1 = round(n * BMAX_1_RATIO)
  nb2 = round(n * BMAX_2_RATIO)
  nb3 = round(n * BMAX_3_RATIO)

  n_actual = nb1 + nb2 + nb3  # Might differ from n due to rounding.

  b_maxs = [1]*nb1 + [2]*nb2 + [3]*nb3  # Construct b_maxs list

  # Construct random weights between each pair of nodes
  weights = {}
  for i in range(n_actual):
    for j in range(i+1, n_actual):
      weights[(i, j)] = random.random()

  # Time the solution, averaged over 10 runs.
  seconds = timeit.timeit(
      lambda: solve_and_print_count(b_maxs, weights), number=10) / 10

  print('Solved for', n_actual, 'nodes in', seconds, 'seconds')


def main(argv: Sequence[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')

  # Try running the benchmark over various graph sizes.
  b_matching_benchmark(5)
  b_matching_benchmark(10)
  b_matching_benchmark(20)
  b_matching_benchmark(40)
  b_matching_benchmark(80)
  b_matching_benchmark(200)


if __name__ == '__main__':
  app.run(main)
