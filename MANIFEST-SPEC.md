# Argos Signature Manifest Specification

## Schema version 1

Each distribution channel exposes one `manifest.json` describing a complete, atomic signature set.

Required top-level fields:

```json
{
  "schema_version": 1,
  "database_version": "YYYY.MM.DD.N",
  "channel": "stable",
  "files": {}
}
```

### `schema_version`

Integer identifying the manifest contract. Clients must reject unsupported schema versions.

### `database_version`

Opaque release identifier for the complete signature set. The recommended format is `YYYY.MM.DD.N`, where `N` allows more than one publication in a day.

### `channel`

Must be either `stable` or `testing` and must match the directory from which the manifest was downloaded.

### `files`

Object keyed by filename. Each entry must contain:

```json
{
  "sha256": "64 lowercase hexadecimal characters",
  "size": 12345
}
```

`size` is the exact byte length of the distributed file.

## Activation requirements

Clients must treat a manifest as one atomic set. All declared files must download and validate before any active signature database is replaced. Files not declared by the manifest must not become active as part of that update.

A client must reject the update when any of the following occurs:

- unsupported `schema_version`;
- invalid channel;
- duplicate or unsafe filename;
- missing declared file;
- unexpected regular file in the channel signature directory;
- size mismatch;
- SHA-256 mismatch;
- database validation failure.

Clients should retain one previously active set for rollback.

## Compatibility

Database line formats belong to the individual Argos database parsers. This manifest schema deliberately does not change existing pipe-delimited signature formats, comments or confidence scoring semantics.
