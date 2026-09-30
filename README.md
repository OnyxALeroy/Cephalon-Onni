# Cephalon Onni

**Cephalon Onni** is a companion web application for *Warframe* that allows players to visualize, manage, and analyze their inventory outside the game. The goal is to provide users with a clean, fast, and modern interface to view their Arsenal, equipment, and progression anytime, anywhere.

The main selling point of the Cephalon Onni are the Warframe profile getter, allowing the users to access their Arsenal, equiment, progression, etc., without launching the game.

---

## Tech Stack

### Frontend

* Vue 3 + TypeScript
* Vite
* Vue Router
* CSS (Scoped styles / CSS Modules / Tailwind planned)

### Backend

* Spring Boot (Java 21)
* PostgreSQL (Hibernate/JPA + Flyway)
* Redis (worldstate cache)
* JWT-based (cookie) authentication
* REST API

---

## Setup Instructions

See [[Development.md]] for detailed setup instructions.

---

## Operations

**Environment variables** — see [.env.example](.env.example). Two that matter in production:

* `JWT_SECRET` — required; the backend refuses to start without a >= 32-byte secret.
* `APP_COOKIE_SECURE` — set to `true` behind TLS so the auth cookie gets the `Secure` flag.

**Creating the first administrator** — there is deliberately no bootstrap endpoint (nothing
admin-gated that a fresh deploy could call without an admin). Register a normal account,
then promote it once, directly in the database:

```sql
UPDATE users SET role = 'Administrator' WHERE email = 'you@example.com';
```

**Running the backend tests** — `cd backend && mvn test` (requires Docker: the integration
tests use Testcontainers to run a real Postgres; no Redis is needed).

---

## Roadmap

* [ ] Inventory display API
* [ ] Equipment details panel
* [ ] Search & filtering system
* [ ] Backend integration
* [ ] Player profile page
* [ ] Missions / Alerts
* [ ] Dark console UI enhancements
* [ ] "Creative mode" weapon modding
* [ ] Event agenda?
* [ ] Easy resource map reader (what is available on each planet)
* [ ] Void relics content searcher
* [ ] Warframe Market (when looking for something, adding the WM as a source with the average price)

---

## Disclaimer

Cephalon Onni is a fan project and is **not affiliated with Digital Extremes**.

*Warframe and all related assets are trademarks of Digital Extremes Ltd.*\
This project does not contain copyrighted assets from the game.

---

## Contribution

Contributions will be welcome once the project enters beta phase.

If you want to help with UI, backend, or Warframe API knowledge — feel free to open an issue or pull request in the future!

---

## Contact

Created by **Onyx** and **Nials**.\
Building a Warframe console outside the Origin System.

---
