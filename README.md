This module implements an algorithm designed for optimal matchings encouraging
informal social connections between team members in a workgroup.

While our company's WFH policy was in place during the COVID-19 pandemic, my
team sought ideas to strengthen social ties and help new hires feel welcomed.
One very successful program involved randomly assigning weekly 15-minute
meetings between team members for a quick chat. However, many participants felt
these random assignments weren't ideal: Newcomers wanted more meetings early on,
to meet more people. Other team members found themselves meeting with their own
close teammates, or with the same person multiple times in just a few weeks!

To address this, we explored an optimal matching algorithm.  The ideal approach
would assign scores to each potential pairing, assigning
higher scores to pairs of participants in different cities, or different
subteams, and lower scores to pairs that had already been assigned
recently. New hires would be assigned multiple pairings
for new hires in their first few months.

After a literature review, I learned this problem is known in the literature as
the **maximum weighted b-matching** problem. Unlike [stable marriage](https://en.wikipedia.org/wiki/Stable_marriage_problem) or [maximum-weighted
matching](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.matching.max_weight_matching.html#networkx.algorithms.matching.max_weight_matching), b-matching allows some nodes to be matched more than once. There is some recent research demonstrating
[polynomial time solutions](https://arxiv.org/abs/1706.07418) for general
b-matching, but I found no easy-to-use open source implementations. We observed
that for the case of small `n`, a solution based on integer programming runs in
only a few seconds on desktop PCs, which makes it well-suited to this
application's requirements.

In addition to the integer programming solver for standard maximum-weighted
b-matching -- `b_matching.maximize_weighted_b_matching` -- this package also
includes a small wrapper `b_matching.inclusive_matching` enforcing the
additional constraint that all nodes must be used in at least one matched pair.
A short proof for the inclusive matching algorithm can be found in
`inclusive_b_matching.md`. The `toy_example` provides a small example
illustrating the use of inclusive matching to assign social meetings across
a tiny but distributed team.

Acknowledgements: Mirkó Visontai provided helpful math research, suggestions,
and code reviews. Bo Zulonas provided the score-based matching idea, original
scoring functions, and useful feedback.

This is not an officially supported Google product.