# ADR 0001 — Modular Monolith First

## Decision

DrunkIt v0.1 uses a modular monolith for the backend.

## Rationale

The MVP has several domains but insufficient evidence to justify operationally independent services. Keeping domains inside one deployable FastAPI application reduces deployment and networking complexity while preserving clear internal boundaries.

## Extraction trigger

A domain may be extracted when measured load, deployment independence, team ownership, failure isolation or integration requirements justify the additional operational complexity.
