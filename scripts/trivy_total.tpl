{{/*
  SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
  SPDX-License-Identifier: AGPL-3.0-only
*/}}

{{- $count := 0 -}}
{{- range . }}
  {{- $count = add $count (len .Vulnerabilities) -}}
{{- end -}}
{{- $count }}
