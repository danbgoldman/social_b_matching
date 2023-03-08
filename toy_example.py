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

"""This example demonstrates a typical use case for social b-matching."""

from collections.abc import Sequence
import dataclasses

from absl import app
from social_b_matching import b_matching


@dataclasses.dataclass
class Person:
  name: str
  group: str
  max_meetings: int


@dataclasses.dataclass
class PreviousMeeting:
  person1: str
  person2: str
  recency: float


PEOPLE = [
    Person("Ahmed", "LA", 1),
    Person("Barbara", "LA", 1),
    Person("Coco", "NY", 1),
    Person("David", "LA", 2),
    Person("Elizabeth", "NY", 1),
    Person("Francois", "NY", 2),
]

PREVIOUS_MEETINGS = [
    PreviousMeeting("Ahmed", "Coco", 2),
    PreviousMeeting("David", "Elizabeth", 1),
    PreviousMeeting("Ahmed", "David", 3),
    PreviousMeeting("Barbara", "Francois", 4),
    PreviousMeeting("Coco", "Francois", 2),
]


def main(argv: Sequence[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError("Too many command-line arguments.")

  # For simplicity, define a mapping from person names to meeting recency.
  pair_to_recency = {
      (meeting.person1, meeting.person2): meeting.recency
      for meeting in PREVIOUS_MEETINGS
  }

  # Calculate the meeting score for all possible pairs of participants:
  weights = {}
  for i in range(len(PEOPLE)):
    person1 = PEOPLE[i]
    for j in range(i + 1, len(PEOPLE)):
      person2 = PEOPLE[j]

      weight = 1.0  # Default weight is 1

      # If two people are in the same group, reduce the score by half.
      if person1.group == person2.group:
        weight *= 0.5

      # The more recently people have met, the lower their meeting score
      pair = (person1.name, person2.name)
      if pair in pair_to_recency:
        recency = pair_to_recency[pair]
        weight *= 1.0 - 2 ** (-recency)  # Exponential decay

      weights[(i, j)] = weight

  # Allow some people to get more than 1 meeting assigned.
  b_maxs = [person.max_meetings for person in PEOPLE]

  # Calculate the optimal set of meetings.
  result = b_matching.inclusive_matching(b_maxs, weights)

  # Print the pairings, along with their groups and how recently they have met.
  for pair in result:
    person1 = PEOPLE[pair[0]]
    person2 = PEOPLE[pair[1]]
    print(
        f"{person1.name} in {person1.group} meets with {person2.name} in"
        f" {person2.group}"
    )
    namepair = (person1.name, person2.name)
    if namepair in pair_to_recency:
      recency = pair_to_recency[(person1.name, person2.name)]
      print(f"They last met {recency} weeks ago.")
    else:
      print("They haven't met before.")
    print()

  # Verify the pairs are inclusive: At most one person didn't have the max
  # number of meetings assigned:
  inclusive, not_max = b_matching.check_inclusive(b_maxs, result)
  if inclusive:
    print("Every person was assigned their maximum number of meetings.")
  else:
    for i in not_max:
      print(
          f"{PEOPLE[i].name} was not assigned their maximum number of meetings."
      )

# Expected output for the dataset above:

# Ahmed in LA meets with Francois in NY
# They haven't met before.
#
# Barbara in LA meets with Elizabeth in NY
# They haven't met before.
#
# Coco in NY meets with David in LA
# They haven't met before.
#
# David in LA meets with Francois in NY
# They haven't met before.
#
# Every person was assigned their maximum number of meetings.

if __name__ == "__main__":
  app.run(main)
