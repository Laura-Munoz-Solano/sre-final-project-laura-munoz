# Screenshots

Evidence of the working deployment. File names are referenced from the main README.

| File | What it shows |
|------|---------------|
| `01-pods-running.png` | `kubectl get pods -A` with the app and monitoring pods running |
| `02-app-metrics.png` | The app's `/metrics` endpoint |
| `03-prometheus-targets.png` | Prometheus > Status > Targets with `sre-demo-app` UP |
| `04-prometheus-query.png` | A PromQL query over `demo_http_requests_total` |
| `05-prometheus-alerts.png` | Prometheus > Alerts with the `sre-demo-app` rules |
| `06-grafana-dashboard.png` | The "SRE Demo App - Golden Signals" dashboard |
| `07-alert-firing.png` | `DemoAppHighErrorRate` firing in Prometheus |
| `08-alertmanager.png` | The alert received in Alertmanager |
| `09-slack-notification.png` | The notification in Slack |
| `10-github-actions.png` | A green CI/CD pipeline run |
