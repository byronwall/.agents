---
title: "AWS-backed runtime configuration — shape brief"
slug: "aws-runtime-config"
phase: shape
status: current
last_updated: "2026-08-11"
---

# AWS-backed runtime configuration — shape brief

## Recommendation

Treat AWS as a pair of storage adapters behind the application's existing configuration lifecycle—not as the new shape of the application. Introduce a small application-facing boundary that can load and persist one validated configuration revision. Keep secret routing inside a coordinator so the rest of the application does not need to know which AWS product stores each field.

Prove the behavior in three increasingly realistic environments: a deterministic in-memory source for application logic and failure cases, LocalStack for the AWS API contract, and one small real-AWS sandbox smoke test for IAM, KMS, account, and endpoint behavior. Keep the current TOML/environment path selectable during rollout.

The material pushback is to **avoid beginning with IAM, deployment wiring, and two real AWS services at once**. That route would bundle application semantics, provider behavior, credentials, and operations into one slow feedback loop. The first useful slice should already demonstrate update → persist → restart using a local source.

## Problem and appetite

- **Problem:** The application needs centrally managed configuration that can change while running and survive restart after the move to AWS.
- **Outcome:** One representative secret and non-secret setting can be read, validated, changed, persisted, activated, and recovered after restart.
- **Appetite:** A bounded integration capability, not a general configuration platform.
- **Not in this shape:** Automated secret rotation, multi-region replication, arbitrary schemas, a new administration UI, broad provider abstraction, or removal of every existing configuration source.

## Core shape

```text
startup / update request
        ↓
existing config parser + validator
        ↓
ConfigurationCoordinator
  ├─ ParameterStorePort  ── fake | LocalStack | AWS
  └─ SecretStorePort     ── fake | LocalStack | AWS
        ↓
validated configuration snapshot
        ↓
current application activation path
```

The coordinator owns which fields are secret, the write order, version checks, and the rule for activating a new snapshot. The ports expose only the semantics the application needs: read named values, persist an expected revision, and return typed failures. They do not expose the full AWS SDK.

The first implementation uses one representative ordinary parameter and one secret. A persisted revision or manifest records which values belong to one coherent snapshot. If the current application guarantees one writer, the first slice may use a simpler version token. If concurrent writers are possible, compare-and-set behavior becomes part of the contract.

## Current fit

- **Reuse:** Existing TOML/environment decoding, validation, runtime mutation, and activation behavior.
- **Add:** A coordinator, narrow parameter and secret ports, deterministic fakes, AWS adapters, and one source-selection setting.
- **Avoid or replace:** The Railway-specific persistence hook becomes an adapter or temporary fallback. AWS SDK calls do not spread through configuration consumers.

## How to make this go better

- **Prove the lifecycle before touching AWS.** Run load, update, write failure, restart, and fallback behavior against deterministic local stores. This makes application errors reproducible in seconds.
- **Separate provider fidelity from IAM fidelity.** Use LocalStack or another supported emulator to test SSM and Secrets Manager request/response behavior. Use a small AWS sandbox smoke test only for credentials, permissions, KMS, endpoint, and account-specific behavior.
- **Introduce one external path at a time.** Prove a non-secret parameter first, then add secret routing without changing the application lifecycle. This prevents two provider integrations from hiding one another's failures.
- **Make partial writes explicit.** Do not activate a new configuration until the whole intended revision is durable. Use a manifest/version record or another commit rule rather than assuming two service writes are atomic.
- **Keep the old source selectable.** A configuration flag or source factory should allow TOML/environment startup while the AWS path is being proven and during rollback.
- **Add diagnostics with the first real adapter.** Log source, revision, duration, and typed failure without logging values. A live integration that cannot explain itself is not ready to become authoritative.

## First proof

- **Question:** Can the current application lifecycle support a durable runtime update without depending on Railway or AWS?
- **Proof:** One focused test harness starts the application with an in-memory configuration source, changes one ordinary and one secret field, recreates the configuration manager, and observes the same validated values.
- **Observe:** Validation behavior, activation timing, revision handling, missing-key behavior, a failed second write, and restart recovery.
- **Pass / fail:** Pass when the application never activates a partial revision, all named failures are deterministic, and the test runs without network or shared infrastructure. Fail if provider concepts leak into consumers or the lifecycle requires deployment to exercise.
- **Deliberately excludes:** AWS credentials, IAM, KMS, production deployment, rotation, broad schema generalization, and cloud persistence.

## Rabbit holes and no-gos

- Building a generic configuration framework before one real setting works.
- Treating SSM and Secrets Manager writes as one atomic provider transaction.
- Reproducing the entire AWS SDK in mocks.
- Using a live AWS account as the routine failure-injection environment.
- Introducing account migration, new administration UI, rotation, and runtime persistence in one slice.
- Logging raw configuration values for diagnostics.

## Serious alternative

If runtime changes are rare and a redeploy is acceptable, deployment-time materialization is simpler and safer: an approved deployment job reads AWS values and starts the application with a complete snapshot. Select that path instead if the “update while running” behavior is merely inherited from Railway rather than a real product or operational requirement.

## What still needs your input

- Must the running application itself be allowed to write secrets, or should secret changes require an operator-controlled path?
- Is there one configuration writer, or must the first release protect against concurrent updates?

## Plan handoff

The implementation plan should begin with the provider-free lifecycle proof, add Parameter Store through a shared contract suite, add secret routing as a separate slice, confirm real AWS permissions with one sandbox smoke test, and only then make the AWS source authoritative behind a reversible rollout switch.
