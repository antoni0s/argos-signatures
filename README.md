# Argos Signatures

Central signature database for the **Argos Network Sentinel** ecosystem.

This repository is intentionally independent from the Argos application and the `argos-sniffer` capture engine. Signature databases can evolve without requiring a new Sentinel or sniffer release.

## Channels

- `stable` — signatures intended for normal deployments.
- `testing` — signatures under evaluation before promotion to stable.

Each channel contains a `manifest.json` and a `signatures/` directory. Clients must validate the manifest, file size and SHA-256 digest before replacing an installed database.

## Database format

Argos signature databases remain plain-text, line-oriented files. Existing pipe-delimited formats, comments and confidence semantics are preserved. The distribution layer does not reinterpret the contents of a database.

## Update model

A client update should follow this order:

1. Download the channel `manifest.json`.
2. Verify `schema_version` compatibility.
3. Download databases to a temporary directory.
4. Verify every SHA-256 digest and declared size.
5. Validate database syntax.
6. Atomically replace the active database set.
7. Keep the previous set available for rollback.

The Sentinel should never partially activate a downloaded signature set.

## Repository layout

```text
argos-signatures/
├── README.md
├── MANIFEST-SPEC.md
├── stable/
│   ├── manifest.json
│   └── signatures/
├── testing/
│   ├── manifest.json
│   └── signatures/
├── tools/
│   └── validate.py
└── .github/
    └── workflows/
        ├── validate.yml
        └── package-release.yml
```

## Versioning

`schema_version` describes the manifest/database contract understood by Argos clients. `database_version` identifies a published signature set and is independent of the Argos application version.

Initial manifest schema: **1**.

Stable releases are packaged as:

```text
argos-signatures-<database_version>.tar.gz
SHA256SUMS
```

The archive contains `manifest.json` and the complete `signatures/` directory, making it suitable for atomic download and installation on OpenWrt.

## Security

The updater is expected to use HTTPS and must verify SHA-256 values from the manifest before activation. A failed download, malformed database, size mismatch or checksum mismatch must leave the currently installed database untouched.

This repository must not contain captures, logs, credentials, API keys, private hostnames, private addressing, user-specific fingerprints or other environment-specific data.
