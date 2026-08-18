# Security Policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability-reporting feature for this repository and include reproduction steps,
affected versions and potential impact.

## Supply-chain policy

Pull requests and releases must pass unit tests, dependency auditing, SBOM generation,
Grype scanning and Trivy scanning. A detected critical vulnerability blocks publishing.
Published images are identified by immutable digest and signed keylessly with Cosign.

