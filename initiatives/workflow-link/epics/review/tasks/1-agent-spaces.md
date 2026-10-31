## 1. Agent spaces and the workflow part

- **Depends on:** `mocap-contracts` `v0.8.0` pinned
- **Contract:** a Film menu command registers an agent: its space code and
  its name (`Film.addSpace`, no `proposals-<code>` part), and adds the
  `workflow` part, creating `workflow.sqlite` with `mocap_contracts.db`
  when it's missing. Codes and names are typed by the creator; nothing is
  inferred. A missing database is a `Problem` with a relink reference,
  like any part.
- **Tests:** register two agents on the sample; `film.json` validates; the
  database opens; a duplicate code refused
