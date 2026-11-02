# Contributing

Thanks for your interest in this project! It's my final project for the SRE Academy, but suggestions and improvements are welcome.

## How to Contribute

1. **Fork the Repository**
   Use the GitHub UI to fork the repo into your own account.

2. **Create a Feature Branch**
   Name your branch clearly to reflect the change.
   Example: `git checkout -b add-latency-panel`

3. **Make Your Changes**
   Be sure to:
   - Follow the existing folder structure and naming.
   - Run the tests and the linter before committing:
     `cd app && pytest && flake8 . --max-line-length=100`
   - Check the chart with `helm lint ./sre-app-chart`.
   - Test the full setup with `./cluster.sh` if you changed the chart.

4. **Commit and Push**
   Example:
   `git add .`
   `git commit -m "Add latency panel to the dashboard"`
   `git push origin add-latency-panel`

5. **Open a Pull Request**
   - Include a descriptive title and a short summary of the change.
   - The CI pipeline has to pass before merging.

## Guidelines

- Write in clear English.
- Never commit secrets (for example the Slack webhook URL).
- New alerts need a `severity` and a `service` label, and a `summary` and `description`.
- Keep the setup reproducible with `cluster.sh` and add cleanup steps for anything new.

---

Thanks again for your contribution!
