# service-catalog-sync

> Automated Backstage catalog hydration — scans repos, infers ownership and tech stack, keeps catalog fresh via CI.

![CI](https://github.com/brianpelow/service-catalog-sync/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)

## Overview

`service-catalog-sync` automates the most painful part of running Backstage —
keeping the catalog up to date. It scans your repositories, infers language,
framework, ownership, and SLO configuration, then generates and pushes
`catalog-info.yaml` files automatically.

Built for platform engineering teams in regulated financial services and
manufacturing who maintain Backstage as their engineering system of record
but struggle with catalog staleness and manual YAML maintenance.

## Commands

| Command | Description |
|---------|-------------|
| `catalog-sync scan` | Scan a repo and infer catalog metadata |
| `catalog-sync generate` | Generate catalog-info.yaml for a repo |
| `catalog-sync sync` | Scan, generate, and push to GitHub |
| `catalog-sync batch` | Process all repos in a directory |

## Quick start

```bash
pip install service-catalog-sync

export GITHUB_TOKEN=your_token
export BACKSTAGE_URL=https://your-backstage.example.com

catalog-sync scan ./my-service
catalog-sync generate ./my-service --output catalog-info.yaml
catalog-sync sync ./my-service --repo org/my-service
```

## Generated catalog-info.yaml

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: Inferred from README
  annotations:
    github.com/project-slug: org/my-service
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: payments-team
  system: payments-platform
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0