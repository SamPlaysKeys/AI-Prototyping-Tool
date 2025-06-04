{{/*
Expand the name of the chart.
*/}}
{{- define "ai-prototyping-tool.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ai-prototyping-tool.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ai-prototyping-tool.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ai-prototyping-tool.labels" -}}
helm.sh/chart: {{ include "ai-prototyping-tool.chart" . }}
{{ include "ai-prototyping-tool.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ai-prototyping-tool.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-prototyping-tool.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ai-prototyping-tool.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ai-prototyping-tool.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config map
*/}}
{{- define "ai-prototyping-tool.configMapName" -}}
{{- printf "%s-config" (include "ai-prototyping-tool.fullname" .) }}
{{- end }}

{{/*
Generate the config.toml content
*/}}
{{- define "ai-prototyping-tool.configToml" -}}
[app]
name = {{ .Values.config.data.app.name | quote }}
version = {{ .Values.config.data.app.version | quote }}
environment = {{ .Values.config.data.app.environment | quote }}
debug = {{ .Values.config.data.app.debug }}

[server]
host = {{ .Values.config.data.server.host | quote }}
port = {{ .Values.config.data.server.port }}
workers = {{ .Values.config.data.server.workers }}
reload = {{ .Values.config.data.server.reload }}

[logging]
level = {{ .Values.config.data.logging.level | quote }}
format = {{ .Values.config.data.logging.format | quote }}
enable_file_logging = {{ .Values.config.data.logging.enable_file_logging }}
log_directory = {{ .Values.config.data.logging.log_directory | quote }}
max_file_size_mb = {{ .Values.config.data.logging.max_file_size_mb }}
max_files = {{ .Values.config.data.logging.max_files }}
enable_trace_ids = {{ .Values.config.data.logging.enable_trace_ids }}

[lm_studio]
base_url = {{ .Values.config.data.lm_studio.base_url | quote }}
api_key = {{ .Values.config.data.lm_studio.api_key | quote }}
auto_detect = {{ .Values.config.data.lm_studio.auto_detect }}
health_check_interval = {{ .Values.config.data.lm_studio.health_check_interval }}
connection_timeout = {{ .Values.config.data.lm_studio.connection_timeout }}
request_timeout = {{ .Values.config.data.lm_studio.request_timeout }}

[model]
default_name = {{ .Values.config.data.model.default_name | quote }}
max_tokens = {{ .Values.config.data.model.max_tokens }}
temperature = {{ .Values.config.data.model.temperature }}
top_p = {{ .Values.config.data.model.top_p }}
retries = {{ .Values.config.data.model.retries }}

[output]
format = {{ .Values.config.data.output.format | quote }}
theme = {{ .Values.config.data.output.theme | quote }}
merge_deliverables = {{ .Values.config.data.output.merge_deliverables }}
include_toc = {{ .Values.config.data.output.include_toc }}
add_metadata = {{ .Values.config.data.output.add_metadata }}
auto_save = {{ .Values.config.data.output.auto_save }}
output_directory = {{ .Values.config.data.output.output_directory | quote }}

[deliverables]
default_types = {{ .Values.config.data.deliverables.default_types | toJson }}
completion_mode = {{ .Values.config.data.deliverables.completion_mode | quote }}
parallel_limit = {{ .Values.config.data.deliverables.parallel_limit }}
template_directory = {{ .Values.config.data.deliverables.template_directory | quote }}

[error_handling]
enable_global_handler = {{ .Values.config.data.error_handling.enable_global_handler }}
user_friendly_messages = {{ .Values.config.data.error_handling.user_friendly_messages }}
include_stack_traces = {{ .Values.config.data.error_handling.include_stack_traces }}
log_errors = {{ .Values.config.data.error_handling.log_errors }}
error_page_template = {{ .Values.config.data.error_handling.error_page_template | quote }}

[security]
enable_cors = {{ .Values.config.data.security.enable_cors }}
allowed_origins = {{ .Values.config.data.security.allowed_origins | toJson }}
api_key_header = {{ .Values.config.data.security.api_key_header | quote }}
rate_limit_requests = {{ .Values.config.data.security.rate_limit_requests }}
rate_limit_window = {{ .Values.config.data.security.rate_limit_window }}

[monitoring]
enable_metrics = {{ .Values.config.data.monitoring.enable_metrics }}
metrics_endpoint = {{ .Values.config.data.monitoring.metrics_endpoint | quote }}
health_endpoint = {{ .Values.config.data.monitoring.health_endpoint | quote }}
ready_endpoint = {{ .Values.config.data.monitoring.ready_endpoint | quote }}
{{- end }}
