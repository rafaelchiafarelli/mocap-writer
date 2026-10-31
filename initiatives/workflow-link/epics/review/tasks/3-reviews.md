## 3. Reviews written on approve, reject and edit

- **Depends on:** 2
- **Contract:** approve writes the value into the item as
  `creator-approved` (source kept, `by` the creator) through
  `Film.writeText` and adds a `Review` `approved`; edit does the same with
  the creator's text and `edited`; reject adds a `Review` `rejected` and
  leaves the bible untouched. Approving one of two competing proposals
  rejects the other. A batch is one database transaction.
- **Tests:** each outcome on the test database: bible, history and review
  rows as stated; a refused bible write leaves no review
