## 2. Open proposals in the review queue

- **Depends on:** 1
- **Contract:** `review.queue` also lists every proposal without a review,
  by scene like the other entries, showing the agent, the field, the value
  and its source (the memo). Two proposals for the same item, field and
  scene are listed together. A proposal for an item no longer in the
  bible is listed as a notice, not approvable.
- **Tests:** queue of a test database with two agents, a shared field, a
  reviewed proposal (not listed) and a dangling item
