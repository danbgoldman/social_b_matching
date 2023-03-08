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

"""Solve for the maximum weighted b-matching of a weighted graph.

See https://en.wikipedia.org/wiki/Matching_(graph_theory) for terminology.

A matching of a graph is a set of edges that touch no common vertices. A
b-matching is similar, but nodes can touch b edges in the matching, where b
can vary per-node.  A maximum matching or b-matching is one that maximizes the
sum of edge weights.

"""

from typing import Mapping, List, Optional, Sequence, Tuple

from absl import logging

from ortools.linear_solver import pywraplp


_Edge = Tuple[int, int]


class SolverError(Exception):
  """The internal solver has a problem."""


def _validate_b_maxs(b_maxs: Sequence[int]):
  """Validate all b_max are positive integers."""
  for b_max in b_maxs:
    if b_max <= 0:
      raise ValueError('B_max values must be greater than zero.')


def _validate_weights(weights: Mapping[_Edge, float], nodes: int):
  """Validate all weights are non-negative and edges are between valid nodes."""
  for edge, weight in weights.items():

    if edge[0] < 0 or edge[1] < 0:
      raise ValueError('Node indices must be non-negative.')

    if edge[0] >= nodes or edge[1] >= nodes:
      raise ValueError('Edge index too high.')

    if weight < 0:
      raise ValueError('Weights must be non-negative.')


def _validate_fully_connected(weights: Mapping[_Edge, float], nodes: int):
  """Validate all node pairs have exactly one edge."""

  for i in range(nodes):
    for j in range(i+1, nodes):
      forward_edge = (i, j) in weights
      backward_edge = (j, i) in weights
      if not (forward_edge or backward_edge):
        raise ValueError(f'Missing edge ({i}, {j})')
      if forward_edge and backward_edge:
        raise ValueError(f'Duplicated edge ({i}, {j})')

  # Handle self-directed edges or other weirdness.
  if len(weights) != nodes * (nodes - 1) / 2:
    raise ValueError('Wrong number of edges.')


def maximize_weighted_b_matching(
    b_maxs: Sequence[int],
    weights: Mapping[_Edge, float],
    b_min: int = 0,
    timeout_ms: Optional[int] = None) -> List[_Edge]:
  """Solve the for maximum weighted b-matching of a weighted graph.

  This function solves for the special case where b_min <= b <= b_max, using
  integer programming.

  Depending on the solver configuration, this approach may not find the optimal
  solution, and almost certainly doesn't have the optimal runtime. But it's easy
  to implement and understand!

  Args:
    b_maxs: a list of maximum integer b values, one per node.
    weights: a dictionary of edge weights, where the keys are pairs of integer
      node indices and the values are the floating point weights.
    b_min: optional minimum b value, must be non-negative. Setting this to a
      value other than zero could result in infeasible solutions.
    timeout_ms: optional maximum time for a solution. Setting this argument may
      result in a suboptimal or infeasible solution.

  Returns:
    A list of selected edges (as pairs of integer node indices), which
    maximizes the sum of weights while guaranteeing that the degree of each
    node is less than or equal to the number of b for that node.

  Raises:
    ValueError: The input values are invalid.
    SolverError: The internal solver could not find a solution, or the solution
        is infeasible.
  """
  _validate_b_maxs(b_maxs)
  _validate_weights(weights, len(b_maxs))
  if b_min < 0:
    raise ValueError('b_min must be non-negative.')

  solver = pywraplp.Solver('SolveMaxWeightedBMatching',
                           pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING)

  # A dictionary of variables, indexed by edges.
  edge_vars = {}

  # A list of variables touching each node, indexed by node.
  edge_vars_on_node = [[] for _ in range(len(b_maxs))]

  # The sum of selected edge weights.
  total_weights = 0

  # Loop through all edges in the graph.
  for edge, weight in weights.items():

    # Each edge is associated with a boolean variable, indicating whether
    # that edge is present in the solution set.

    # (BoolVar is an abstract type that "looks like" a variable, but can only
    # be used in linear expressions and inequalities as input to the solver.)
    edge_var = solver.BoolVar(f'edge_{edge[0]}_{edge[1]}')
    edge_vars[edge] = edge_var

    # Keep track of which edges touch each node.
    edge_vars_on_node[edge[0]].append(edge_var)
    edge_vars_on_node[edge[1]].append(edge_var)

    # Keep track of total edge weight to be maximized.
    total_weights += weight * edge_var

  # Loop through all nodes in the graph.
  for node_index in range(len(b_maxs)):
    # Add a constraint such that the sum of selected edges is <= b_max.
    solver.Add(
        sum(edge_vars_on_node[node_index]) <= b_maxs[node_index],
        f'b_max_{node_index}')
    if b_min:
      solver.Add(
          sum(edge_vars_on_node[node_index]) >= b_min, f'b_min_{node_index}')

  # We're solving for maximum total_weights.
  solver.Maximize(total_weights)

  # Solve!
  if timeout_ms is not None:
    solver.set_time_limit(timeout_ms)
  status = solver.Solve()
  if status != solver.OPTIMAL:
    if status == solver.FEASIBLE:
      logging.warning('A potentially suboptimal solution was found.')
    else:
      raise SolverError('The solver could not solve the problem.')

  # Verify the validity of the solution by checking that all constraints in the
  # model are satisfied within tolerance epsilon. This is good practice;
  # numerical issues and bugs in the solver are rare but can happen.
  epsilon = pywraplp.MPSolverParameters.kDefaultPrimalTolerance
  log_errors = True
  if not solver.VerifySolution(epsilon, log_errors):
    # VerifySolution reports additional information in the logging output.
    raise SolverError('The solution does not satisfy the constraints!')

  return [edge for (edge, var) in edge_vars.items() if var.solution_value()]


def inclusive_matching(b_maxs: Sequence[int],
                       weights: Mapping[_Edge, float],
                       timeout_ms: Optional[int] = None) -> List[_Edge]:
  """Solve the for most *inclusive* b-matching of a weighted graph.

  This is usually the same as the maximum-weighted b-matching with min_b = 1,
  but when no feasible solution exists under that constraint, then min_b is set
  to 0.  A proof of how and why this works can be found in
  inclusive_b_matching.md.

  Args:
    b_maxs: a list of maximum integer b values, one per node.
    weights: a dictionary of edge weights, where the keys are pairs of integer
      node indices and the values are the floating point weights.
    timeout_ms: optional maximum time for a solution. Setting this argument may
      result in a suboptimal or infeasible solution.

  Returns:
    A list of selected edges (as pairs of integer node indices), which
    maximizes the sum of weights while guaranteeing that the degree of each
    node is less than or equal to the number of b for that node.

  Raises:
    ValueError: The input values are invalid.
    SolverError: The internal solver could not find a solution, or the solution
        is infeasible.
  """

  _validate_fully_connected(weights, len(b_maxs))

  b_min = 1 if max(b_maxs) > 1 else 0
  return maximize_weighted_b_matching(b_maxs, weights, b_min, timeout_ms)


def check_inclusive(b_maxs: Sequence[int],
                    solution: Sequence[_Edge]):
  """Verify a solution meets the inclusive matching conditions.

  That is, that every node has at least one match, and at most one node has
  one less than its b_max number of matches.

  Args:
    b_maxs: a list of maximum integer b values, one per node.
    solution: a list of matched edges to check.

  Returns:
    A tuple: true or false if it's not inclusive, and a list of nodes
    with num_matches != b_max

  Raises:
    ValueError: the input edges include bad nodes 0 < i < len(b_maxs).
  """

  n = len(b_maxs)
  match_counts = [0] * n
  for p, q in solution:
    if p < 0 or p >= n: raise ValueError(f'Bad node {p}')
    if q < 0 or q >= n: raise ValueError(f'Bad node {q}')
    match_counts[p] += 1
    match_counts[q] += 1

  not_max = []
  success = True
  for i, (count, b_max) in enumerate(zip(match_counts, b_maxs)):
    if count != b_max:
      not_max.append(i)
    if count > b_max:
      success = False
  if len(not_max) > 1:
    success = False
  if len(not_max) == 1 and match_counts[not_max[0]] + 1 != b_maxs[not_max[0]]:
    success = False

  return success, not_max
