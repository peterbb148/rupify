# Public Release Checklist

This checklist captures the repository-level work and GitHub settings required before the repo is
renamed to `rupify` and made public.

## Repository Files

The repo should contain:

- a chosen open-source `LICENSE`
- `.github/CODEOWNERS`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`

## GitHub Branch Protection

Apply branch protection to `main` before making the repository public.

Recommended minimum settings:

- require a pull request before merging
- require at least one approval before merging
- dismiss stale approvals when new commits are pushed
- require status checks to pass before merging
- require branches to be up to date before merging
- block direct pushes to `main`
- include administrators in branch protection

## Required Status Checks

At minimum, protect the repository with the automated verification that proves the packaged CLI and
rendering workflow still work:

- `test`

Once the repository is public and CodeQL can run, also require:

- `codeql-analyze`

If CI is later expanded, keep branch protection aligned with the actual required checks instead of
leaving settings stale.

## Repository Settings Before Public Launch

- rename the repository to `rupify`
- confirm the default branch is `main`
- confirm branch protection is active on `main`
- confirm `test` is required before merge
- enable issues
- enable pull requests
- disable force pushes to protected branches
- disable branch deletion on protected branches
- confirm the repository description reflects the current product scope

## Release Readiness Review

Before making the repository public, verify:

- the README describes the current supported workflows accurately
- example bundles are up to date with the shipped model contract
- no private/internal-only references remain in the main documentation
- archived historical planning material is clearly separated from active docs
- the chosen license is present and correct
- the `test` workflow has run successfully at least once on GitHub

## Post-Rename Follow-Up

After renaming the repository:

- confirm links in the README and docs still resolve
- confirm open PR and issue references still render correctly
- confirm package install and `uv run` workflows still work from a fresh clone
- enable CodeQL code scanning if it is not already active
- add `codeql-analyze` to the required checks on `main`
