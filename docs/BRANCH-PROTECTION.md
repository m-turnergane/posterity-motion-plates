# Owner click-steps: make passing CI mandatory for master (GitHub web UI; agents cannot do this)

1. Repo > **Settings** > **Branches** > **Add branch protection rule** (or *Add classic branch protection rule*).
2. **Branch name pattern:** `master`.
3. Tick **Require a pull request before merging** (optional: 1 approval; tick **Require review from Code Owners** to protect `approvals/`).
4. Tick **Require status checks to pass before merging**, tick **Require branches to be up to date before merging**, then in the search box add the check **`ci-gate`** (job `ci-gate` of workflow `ci`; it only turns green when both matrix jobs `test (extras dev,masks)` and `test (extras dev)` pass). The checks only appear in the search list after the workflow has run once on a PR or push.
5. Tick **Do not allow bypassing the above settings** (and leave "Allow force pushes" / "Allow deletions" off). Click **Create** / **Save changes**.
6. Optional, if using Rulesets (Settings > Rules > Rulesets > New branch ruleset): target `master`, enable *Require status checks to pass* with `ci-gate`, *Require a pull request*, *Block force pushes*.
7. Optional CODEOWNERS: add a file `.github/CODEOWNERS` with the line `/approvals/ @<owner-github-login>` so only the owner can approve changes there.
