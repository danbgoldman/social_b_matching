# Inclusive b-matching

When using b-matching to assign pairs of matches, it can happen that one node is
left "uncovered" by the optimal matching - that is, one node is unmatched. We'd
like to find the optimal **inclusive b-matching** that covers all nodes iff such
a constraint is satisfiable. This doc explores the conditions of satisfiability.

It turns out that **at most** one person doesn't get any match:

> **Lemma 1:** Given a maximum weighted b-matching on a fully-connected graph
> with all positive weights, there is at most one node that is not covered by at
> least one match.
>
> **Proof:** Suppose there are two nodes covered by no matches. There exists an
> edge with positive weight between those nodes, so appending that edge to the
> maximum-weighted matching has greater weight than the given maximum matching,
> which is a contradiction of the givens. Therefore, there can be no more than
> one such node.

Suppose we add constraints such that each node must be covered at least once. Is
there always a matching that satisfies these constraints? No: consider the case
of 3 nodes with max b-value 1. Only one match is possible, so a third wheel will
always be left out.

Now suppose that we add the condition that **at least one node has max-b-value
greater than 1**. It turns out this this is a **sufficient condition** to
guarantee that the constraints are satisfiable:

> **Lemma 2**: Given a maximum weighted b-matching on a fully-connected graph
> with all positive weights and one uncovered node p, all other nodes are fully
> covered - there are exactly max-b adjacent edges for all other nodes in the
> matching.
>
> **Proof**: If there were another node q without max-b edges in the matching,
> we could add an edge pq to increase the sum of weights, contradicting the
> givens. Therefore all other nodes beside p are fully covered.

> **Theorem 1**: Given a fully-connected graph with all positive weights and at
> least one node q with max-b value greater than 1, there exists a b-matching
> that covers all nodes.
> 
> **Proof**: Consider the maximum-weighted b-matching of this graph. There are
> two cases:
> 1. The maximum-weighted b-matching covers all nodes, satisfying the condition.
> 2. The maximum-weighted b-matching leaves exactly one node p uncovered, by
>    Lemma 1. And by Lemma 3, all other nodes have a number of edges in the
>    matching equal to their max b-value. Since there is at least one node q
>    with max-b value greater than 1, p can “steal” one of the two edges
>    covering node q. In this updated matching, p now has 1 covered edge, and q
>    has at least 1 covered edge. Thus all nodes again have 1 or more covered
>    edges. Note that this matching may have *lower total weight* than the
>    non-inclusive maximum weighted b-matching, because the newly added edge may
>    have lower weight than the one it replaced, but it’s still possible to find
>    such a matching.
>
> **QED.**

Thus, we can find an **optimal inclusive matching** by checking the list of max
b-values to see if any node has max b-value greater than 1. If so, we can add
constraints to require each node to be covered once, and still ensure
satisfiability of the constraints. Otherwise, we just solve without the
minimum-cover constraint. Since all nodes have a max b-value of 1, the optimal
match will have n/2 matches. If n is even, every node will get matched, and if n
is odd, then one node will be left out. (And there is no way to avoid it without
breaking some other constraint.)

This inclusive matching algorithm is implemented here as
`b_matching.inclusive_matching`.


