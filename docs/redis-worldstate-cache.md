# Redis in the worldstate path: now only a cold-start mirror

Status: open question, nothing changed yet.

## How it works today

`WorldStateCacheService` has three layers:

| Layer | Written | Read |
|---|---|---|
| In-memory parsed `WorldState` | on every upstream change (`update()`) | first choice, every request |
| Redis `worldstate:data` / `:etag` / `:fetched_at` | on every upstream change (~1 MB) | only when memory is empty |
| Postgres `worldstate_cache` (single row) | on every upstream change (~1 MB) | when memory and Redis are both empty; also the first choice for the ETag seed |

Before commit a4212f1, Redis was the hot read path: every `/api/worldstate` request read and
re-parsed the payload from Redis. With the in-memory copy added, Redis is only read when memory
is empty, which means only the first read after a process start.

## Why Redis is now almost dead weight

- **Memory fills almost at once.** `WorldStateFetcher` polls with `initialDelay = 0`, so the
  cache is filled within seconds of boot. That comes either from a 200 response or from the
  first `get()`.
- **Postgres already covers a cold start.** If memory is empty, the DB row has the same
  payload. Redis only saves one ~1 MB row read, once per process lifetime, which is negligible.
- **The ETag fallback is redundant.** `persistedEtag()` reads the DB first. Redis is used only
  when the row is missing, and then Redis almost certainly has no data either.

## What it costs

- An extra `redis` service in `docker-compose.yml` and the `spring-boot-starter-data-redis`
  dependency.
- Around 60 lines in `WorldStateCacheService`: `writeRedis`, `backfillRedis`,
  `rawPayloadFromRedis` and the Redis branch of `persistedEtag`.
- One more failure mode to reason about. It's best-effort, but it still logs warnings and
  adds a connection pool.
- ~1 MB written on every upstream change, for data that is almost never read back.

`WorldStateCacheService` is the only Redis user in the backend. Nothing else (auth, rate
limiting, sessions) depends on it: JWT auth is stateless.

## When Redis would earn its place

If the backend is ever **scaled horizontally**. The current design would not work as-is:

- Every instance runs its own `WorldStateFetcher`, so N instances mean N times the upstream traffic.
- Every instance keeps its own in-memory copy, updated only by its own poller.

Getting real value from Redis would need:

1. **A single poller.** Use a Redis lock (like the old backend's) or ShedLock with the Redis or JDBC provider.
2. **Cross-instance invalidation.** The poller publishes on a Redis pub/sub channel, and the
   other instances drop or reload their in-memory copy. Redis then becomes the shared source
   between instances.

## Options

- **A. Remove Redis from the worldstate path** (and from compose and the pom if nothing else
  needs it). The chain becomes memory → Postgres. This is the simplest option and loses nothing
  measurable on a single instance.
- **B. Keep it as a documented cold-start mirror.** No work, but it keeps the costs above for
  almost no benefit.
- **C. Redesign it for multi-instance use** (single poller plus pub/sub invalidation). Worth it
  only when a second backend instance is actually planned.

## Recommendation

**A** while the app is deployed as a single instance, which is the case with the current
`docker-compose.yml`. If scaling out becomes a goal, go to **C**. Adding Redis back then is
cheap, and the required design is different from today's mirror anyway.
