{{/*
  SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
  SPDX-License-Identifier: AGPL-3.0-only
*/}}

{{- $severities := dict "UNKNOWN" 0 "LOW" 1 "MEDIUM" 2 "HIGH" 3 "CRITICAL" 4 -}}
{{- $max := 0 -}}
{{- range . }}
  {{- range .Vulnerabilities }}
    {{- $sev := index $severities .Severity -}}
    {{- if gt $sev $max }}{{ $max = $sev }}{{ end -}}
  {{- end }}
{{- end }}

{{- if eq $max 0 }}
None
{{- else }}
  {{- range $k, $v := $severities }}
    {{- if eq $v $max }}{{ $k }}{{ end }}
  {{- end }}
{{- end }}
