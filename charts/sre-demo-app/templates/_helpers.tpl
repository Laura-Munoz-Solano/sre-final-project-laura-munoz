{{/* Common labels applied to every object. */}}
{{- define "sre-demo-app.labels" -}}
app.kubernetes.io/name: sre-demo-app
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Labels used to select the pods. */}}
{{- define "sre-demo-app.selectorLabels" -}}
app.kubernetes.io/name: sre-demo-app
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
