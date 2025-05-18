package trivy

__rego_metadata__ := {
  "id": "TRIVY-BLOCKED-VULNS",
  "title": "Trivy Medium+ Vulnerabilities",
  "severity": "MEDIUM",
  "type": "Vulnerability",
}

deny[message] {
  some i
  some j
  vuln := input.Results[i].Vulnerabilities[j]
  upper(vuln.Severity) == "MEDIUM"
  message := sprintf("MEDIUM VULNERABILITY FOUND: %s (Pkg: %s)", [vuln.VulnerabilityID, vuln.PkgName])
}

deny[message] {
  some i
  some j
  vuln := input.Results[i].Vulnerabilities[j]
  upper(vuln.Severity) == "HIGH"
  message := sprintf("HIGH VULNERABILITY FOUND: %s (Pkg: %s)", [vuln.VulnerabilityID, vuln.PkgName])
}

deny[message] {
  some i
  some j
  vuln := input.Results[i].Vulnerabilities[j]
  upper(vuln.Severity) == "CRITICAL"
  message := sprintf("CRITICAL VULNERABILITY FOUND: %s (Pkg: %s)", [vuln.VulnerabilityID, vuln.PkgName])
}

