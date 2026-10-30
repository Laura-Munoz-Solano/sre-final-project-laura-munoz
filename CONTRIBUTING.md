# Contributing

Thanks for your interest in improving this project. Contributions of any size
are welcome: bug reports, documentation fixes, new alerts or dashboard panels.

## Reporting issues

Open a GitHub issue and include:

- what you expected to happen and what happened instead
- steps to reproduce (commands, values files)
- versions of Minikube, Kubernetes, Helm and the chart

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r app/requirements-dev.txt
pytest app            # unit tests
flake8 app            # lint
helm lint charts/sre-demo-app
```

To try your change end to end, run `./scripts/setup.sh` against a local
Minikube cluster.

## Pull requests

1. Fork the repository and create a branch from `main`
   (`feature/<short-name>` or `fix/<short-name>`).
2. Keep each pull request focused on a single change.
3. Add or update tests when you change application behaviour.
4. Update the README when you change deployment steps, metrics or alerts.
5. Make sure the CI pipeline is green before asking for a review.

## Commit messages

Use short, imperative messages, ideally following
[Conventional Commits](https://www.conventionalcommits.org/):
`feat: add saturation alert`, `fix: correct p95 query`, `docs: update README`.

## Conventions

- **Metrics** use the `demo_` prefix, base units (seconds, bytes) and
  low-cardinality labels (route templates, never raw paths or IDs).
- **Alerts** must have `severity` and `service` labels plus `summary` and
  `description` annotations, and should be actionable.
- **Secrets** (such as the Slack webhook URL) are never committed.

## Code of conduct

Be respectful and constructive. Harassment of any kind is not tolerated.
