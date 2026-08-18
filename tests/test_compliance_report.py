from scripts.compliance_report import build_report


def test_report_passes_without_critical_vulnerabilities() -> None:
    report = build_report(
        {"packages": [{}, {}], "documentNamespace": "example"},
        {"matches": [{"vulnerability": {"severity": "High"}}]},
    )
    assert report["sbom"]["packages"] == 2
    assert report["decision"] == "PASS"


def test_report_fails_on_critical_vulnerability() -> None:
    report = build_report(
        {"packages": []},
        {"matches": [{"vulnerability": {"severity": "Critical"}}]},
    )
    assert report["decision"] == "FAIL"

