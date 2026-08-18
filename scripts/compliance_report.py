"""Create human- and machine-readable supply-chain compliance reports."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def package_count(sbom: dict[str, Any]) -> int:
    return len(sbom.get("packages", []))


def vulnerability_counts(grype: dict[str, Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for match in grype.get("matches", []):
        severity = match.get("vulnerability", {}).get("severity", "Unknown")
        counts[str(severity).upper()] += 1
    return counts


def build_report(sbom: dict[str, Any], grype: dict[str, Any]) -> dict[str, Any]:
    counts = vulnerability_counts(grype)
    critical = counts.get("CRITICAL", 0)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "policy": {
            "name": "critical-vulnerability-release-gate",
            "maximum_critical_vulnerabilities": 0,
        },
        "sbom": {
            "format": "SPDX JSON",
            "packages": package_count(sbom),
            "document_namespace": sbom.get("documentNamespace", "unknown"),
        },
        "vulnerabilities": dict(sorted(counts.items())),
        "decision": "PASS" if critical == 0 else "FAIL",
    }


def markdown(report: dict[str, Any]) -> str:
    vulnerabilities = report["vulnerabilities"]
    severity_rows = "\n".join(
        f"| {severity.title()} | {count} |"
        for severity, count in vulnerabilities.items()
    )
    if not severity_rows:
        severity_rows = "| None detected | 0 |"
    return f"""# Software Supply-Chain Compliance Report

**Decision:** {report["decision"]}  
**Generated:** {report["generated_at"]}  
**Policy:** Block release when one or more critical vulnerabilities are detected.

## SBOM Evidence

- Format: {report["sbom"]["format"]}
- Packages catalogued: {report["sbom"]["packages"]}
- Document namespace: {report["sbom"]["document_namespace"]}

## Vulnerability Summary

| Severity | Count |
|---|---:|
{severity_rows}

## Enforced Controls

- SPDX and CycloneDX SBOM artefacts generated from the built image.
- Grype scans the SPDX SBOM and enforces the critical-severity policy.
- Trivy independently scans the container image for OS and library CVEs.
- Successful main-branch images are published by digest, keylessly signed with Cosign,
  and accompanied by GitHub build-provenance attestation.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sbom", type=Path, required=True)
    parser.add_argument("--grype", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()

    report = build_report(load_json(args.sbom), load_json(args.grype))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(f"Supply-chain policy decision: {report['decision']}")
    return 0 if report["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

