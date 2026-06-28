# Security Policy

## Supported Versions

This project is maintained as part of an academic and research effort. Security fixes are applied
to the latest `main` branch.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public issue**. Instead, report it
privately to the maintainer through GitHub (open a private security advisory under the *Security*
tab, or contact the repository owner directly).

Please include:

- A description of the vulnerability and its impact.
- Steps to reproduce it.
- Any relevant logs or configuration.

You can expect an acknowledgement within a reasonable time frame. Responsible disclosure is
appreciated: please allow time for a fix before any public disclosure.

## Scope notes

- This software handles live audio/video streams and a TCP control interface (port 9999) with no
  authentication by design; it is intended to run on a trusted local network. Do not expose the
  control or source ports directly to the public internet.
- Never commit real credentials. Kubernetes secrets are provided as `*.example` templates only.
