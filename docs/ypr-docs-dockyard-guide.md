# YPR Dockyard Guide

## Overview
This document outlines the setup and usage of our internal Python package management system using AWS CodeArtifact.

All private packages (e.g., `ypr-db`, `ypr-skyhawk`) are built locally, uploaded to our artifact repository (`ypr-dockyard/pypi-cargo`), and installed across projects as needed.

---

## Naming Conventions

| Component  | Name          |
|:-----------|:--------------|
| Domain     | `ypr-dockyard` |
| Repository | `pypi-cargo`  |

---

## Initial Setup

1. Install Required Tools:

    ```bash
    pip install twine build
    ```

2. Configure AWS CLI default region (optional):

    ```bash
    aws configure set region us-east-1
    ```

---

## Creating the CodeArtifact Resources (One-Time)

1. Create Domain:

    ```bash
    aws codeartifact create-domain --domain ypr-dockyard --region us-east-1
    ```

2. Create Repository:

    ```bash
    aws codeartifact create-repository --domain ypr-dockyard --repository pypi-cargo --region us-east-1
    ```

---

## Authentication

Authentication is required for both uploading and installing packages.  
Tokens expire approximately every 12 hours.

Run these commands as needed:

```bash
aws codeartifact login --tool pip --domain ypr-dockyard --repository pypi-cargo --region us-east-1

aws codeartifact login --tool twine --domain ypr-dockyard --repository pypi-cargo --region us-east-1
```

### Bash Aliases

```bash
alias loginpip="aws codeartifact login --tool pip --domain ypr-dockyard --repository pypi-cargo --region us-east-1"

alias logintwine="aws codeartifact login --tool twine --domain ypr-dockyard --repository pypi-cargo --region us-east-1"
```

---

## Building and Publishing a Package

1. Navigate to your package directory (e.g., `data-access/db/`).

2. Build the package:

    ```bash
    python -m build
    ```

3. Upload the built package:

    ```bash
    twine upload --repository codeartifact dist/*
    ```

---

## Installing Packages from Dockyard

1. Configure pip to use the repository by updating `~/.config/pip/pip.conf`:

    ```ini
    [global]
    extra-index-url = https://ypr-dockyard-ACCOUNTID.d.codeartifact.us-east-1.amazonaws.com/pypi/pypi-cargo/simple/
    ```

    Replace `ACCOUNTID` with your AWS account ID.

2. Then install packages normally:

    ```bash
    pip install ypr-db
    pip install ypr-skyhawk
    ```

---

## Best Practices

- Always bump version numbers when uploading new package versions.
- Authenticate at the start of your dev session if needed.
- Keep documentation (`/docs/`) updated when processes change.
- Prefer small, focused packages over monolithic ones for better reuse.

---

## Future Enhancements

- Automate builds and uploads using GitHub Actions.
- Front CodeArtifact with CloudFront for a custom domain (e.g., `packages.ypr.com`).
- Version-lock dependencies to avoid surprises across environments.