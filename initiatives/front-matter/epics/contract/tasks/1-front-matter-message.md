## 1. The front_matter message

- **Type:** code, in `mocap-contracts`, then the submodule pin here
- **Depends on:** `mocap-contracts` `v0.6.0` (`common.harpia`'s `Flag`)
- **Contract:**
  - In: the decisions in `../../../front-matter.md`
  - Requires: `front_matter.harpia` with `FrontMatter { TitlePage title;
    Overview overview; Pitch pitch; Argument argument; }`:
    `TitlePage { title, subtitle, episode (string, may be empty), author,
    repeteable co_authors, email }`; `Overview { Flag include; Flag cast;
    Flag sets; Flag acts }` (what to compute, nothing typed);
    `Pitch { Flag include; pitch; logline; target_audience }`;
    `Argument { Flag include; text }`; every field written, empty
    strings allowed; file `settings/front-matter.json` in the writer's
    `settings` folder (a new part `front-matter` in a new film's
    `DEFAULT_PARTS`; an older film without it gets the part added on
    first save); a fixture and an invalid fixture; released in `v0.7.0`
    with `scene_index` and `change_set` (preprod-link/contract)
  - Delivers: `mocap_contracts.FrontMatter`, from_json / to_json
- **Pre-work:** none
- **Tests:** the fixture round-trips; an unknown field is refused
