# SBOM & Container Supply-Chain Security Pipeline

[![Secure software supply chain](https://github.com/advithh-n/sbom-container-supply-chain-pipeline/actions/workflows/supply-chain.yml/badge.svg)](https://github.com/advithh-n/sbom-container-supply-chain-pipeline/actions/workflows/supply-chain.yml)

An end-to-end DevSecOps reference implementation for software deployed into
high-assurance and critical-infrastructure environments. A small grid-asset API is
containerised, tested, inventoried, independently scanned, policy-gated, published by
immutable digest, signed and attested.

## Security architecture

~~~mermaid
flowchart LR
    A[Git push or pull request] --> B[Lint, tests and pip-audit]
    B --> C[Hardened non-root Docker build]
    C --> D[Syft SPDX and CycloneDX SBOMs]
    D --> E[Grype SBOM policy gate]
    C --> F[Trivy image and secret scan]
    E --> G{Critical CVE?}
    F --> G
    G -- Yes --> H[Block release]
    G -- No --> I[Publish immutable digest to GHCR]
    I --> J[Cosign keyless signature]
    J --> K[Build-provenance attestation]
    D --> L[Compliance evidence bundle]
    E --> L
    F --> L
~~~

## Enforced controls

- **Software inventory:** Syft produces both SPDX JSON and CycloneDX JSON SBOMs.
- **Independent vulnerability checks:** Grype scans the SPDX SBOM; Trivy scans the
  built image and repository.
- **Policy as code:** any critical vulnerability blocks the release.
- **Provenance:** successful main-branch images are pushed by digest and signed using
  GitHub OIDC and Sigstore/Cosign—no long-lived signing key.
- **Attestation:** GitHub build provenance binds the source workflow to the image digest.
- **Runtime hardening:** digest-pinned Chainguard build/runtime stages, non-root UID
  65532, read-only filesystem, dropped Linux capabilities, no-new-privileges and
  bounded process/memory resources.
- **Audit evidence:** the workflow retains SBOMs, scan results and JSON/Markdown
  compliance reports.

## Run locally

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
ruff check .
pytest
docker compose up --build
~~~

Then query:

~~~bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/grid/summary
~~~

## Verify a published image

After a successful main-branch workflow, copy the digest from GHCR:

~~~bash
cosign verify \
  --certificate-identity-regexp="https://github.com/advithh-n/sbom-container-supply-chain-pipeline/.github/workflows/supply-chain.yml@refs/heads/main" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/advithh-n/sbom-container-supply-chain-pipeline@sha256:<digest>
~~~

## Compliance report

The report generator consumes Syft SPDX JSON and Grype JSON:

~~~bash
python scripts/compliance_report.py \
  --sbom artifacts/sbom.spdx.json \
  --grype artifacts/grype-results.json \
  --json-output artifacts/compliance-report.json \
  --markdown-output artifacts/compliance-report.md
~~~

This project demonstrates a reference control plane, not a production electricity-grid
system. Production adoption would additionally require approved registries, VEX handling,
change control, secrets management, environment promotion and organisation-specific risk
acceptance.
