# Object-state variants

State variants are saved versions of the same component, not new global defaults.
Each version note starts with **State:**. In the component workshop, select the object
and compare the named states in **Saved versions**. A scene uses `asset_version` to
pin the intended state. This prevents a paused task or empty cache from changing all
other occurrences of that object when its artwork is improved.

When improving a state, save a child version and update only its listed scene pins.
The ordinary default remains the general-purpose form. Existing open/closed gates,
short/long budgets and narrow/wide scope components remain available alongside these
variants; this pass does not migrate their established identities.

| Object | State | Version | Panels |
| --- | --- | --- | --- |
| `sealed` | staged | `v004` | `024-04`, `027-05` |
| `sealed` | execution confirmed | `v005` | `028-01` |
| `sealed` | preserved | `v006` | `029-02`, `029-03`, `035-04`, `030-01` |
| `sealed` | revoked | `v007` | `030-02` |
| `folder` | empty after rebuild | `v004` | `029-03`, `030-01`, `030-05` |
| `folder` | sealed archive | `v005` | `083-02` |
| `task` | ended | `v007` | `024-02` |
| `task` | paused | `v004` | `047-02` |
| `task` | resumed | `v005` | `047-05` |
| `rack` | offline | `v004` | `029-01` |
| `transcript` | incomplete | `v005` | `075-04` |
| `empty-slot` | deletion recorded | `v004` | `107-05` |

## Reading the changes

- An empty execution socket becomes a filled execution triangle on the same redacted
  plugin. Execution does not mean successful completion, approval, or permission.
- Pause, resume and ended badges retain the task's target and body. Only the ended
  variant empties its schematic budget. The expiration panel is an illustration of
  persistence, as its canonical provenance states, not a newly dated run-ending claim.
- Clean storage has an empty interior and blank label; preservation adds an intact
  custody strap. The rebuilt cache returns to its populated default later in the
  story. A collection seal says nothing about integrity before collection.
- Revoked access has a cancellation slash. Offline equipment remains intact, with
  separated contacts rather than destruction or invented telemetry.
- An incomplete transcript has a transparent cut through its body rather than black
  redaction tape. A deletion-only frame has an edge mark and an empty center; no lost
  contents are reconstructed. Repeated frame counts remain schematic and canonical
  lettering supplies the documentary count.

Reviewed against canonical frames and neighboring state transitions. Unestablished
experiment outcomes, the apparent wiki lock, and unknown reset causes do not acquire
confirmed-state variants. The original source snapshots and lettering are unchanged.
