# SPEC-007: Identity and Access Management (IAM) Bounded Context Specification

**Status:** PROPOSED  
**Date:** 2026-09-21  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Governing ADR:** [`docs/adr/ADR-018-identity-and-access-management-bounded-context-and-sveltekit-bff.md`](../adr/ADR-018-identity-and-access-management-bounded-context-and-sveltekit-bff.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Objective & Scope

This specification defines the exact contracts, domain rules, ports, adapters, and acceptance criteria for establishing the **Identity & Access Management (IAM)** Bounded Context (`src/identity/`) in the PES Modular Monolith. 

It provides authentication, account management, personal access token (PAT) issuance, and session governance for both the **SvelteKit Presentation BFF** and headless consumers (CLI and background workers).

---

## 2. Ubiquitous Language (IAM Context)

- **Principal**: An authenticated subject (human user or automated service) with an identified security context.
- **Personal Access Token (PAT)**: A high-entropy, opaque string (`cresmo_pat_<base64url>`) used for machine-to-machine authentication by CLI and workers, stored only as an immutable SHA-256 hash.
- **HashedPassword**: A cryptographically formatted string generated via the Argon2id algorithm, encapsulating salt, cost parameters, and hash bytes.
- **Session**: A server-tracked, time-bounded interaction state linking a client device to an authenticated user.
- **BFF (Backend-for-Frontend)**: A presentation-tier server (SvelteKit) that translates browser session cookies into internal authorization tokens for downstream API calls.

---

## 3. Domain Model (`src/identity/domain/`)

### 3.1 Value Objects (`value_objects.py`)

1. **`UserId`**:
   - UUID4/string representation, immutable. Rejects invalid formats.
2. **`Email`**:
   - Normalized (lowercase, trimmed). Validates RFC 5322 structure.
3. **`HashedPassword`**:
   - Encapsulates Argon2id hash string (`$argon2id$v=19$m=...`). Never exposes plaintext passwords.
4. **`Role`**:
   - Enum with values: `ADMIN`, `USER`, `SERVICE_ACCOUNT`, `VIEWER`.
5. **`Scope`**:
   - Fine-grained permission strings (e.g. `cresmo:read`, `cresmo:write`, `cresmo:sync`, `iam:admin`).
6. **`TokenHash`**:
   - Hex-encoded SHA-256 hash of a Personal Access Token.

### 3.2 Entities & Aggregates (`entities.py`)

1. **`User` (Aggregate Root)**:
   - `id: UserId`
   - `email: Email`
   - `hashed_password: HashedPassword`
   - `roles: frozenset[Role]`
   - `is_active: bool`
   - `created_at: datetime`
   - `updated_at: datetime`
   - Invariants: Cannot modify credentials if `is_active == False`.
2. **`PersonalAccessToken` (Entity)**:
   - `id: str`
   - `user_id: UserId`
   - `name: str`
   - `token_prefix: str` (first 8 chars for user identification, e.g. `cresmo_p...`)
   - `token_hash: TokenHash`
   - `scopes: frozenset[Scope]`
   - `created_at: datetime`
   - `expires_at: datetime | None`
   - `last_used_at: datetime | None`
   - `is_revoked: bool`

---

## 4. Application Layer (`src/identity/application/`)

### 4.1 Abstract Ports (`ports.py`)

```python
class UserRepositoryPort(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...
    @abstractmethod
    def get_by_id(self, user_id: UserId) -> User | None: ...
    @abstractmethod
    def get_by_email(self, email: Email) -> User | None: ...

class PasswordHasherPort(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> HashedPassword: ...
    @abstractmethod
    def verify(self, plain_password: str, hashed: HashedPassword) -> bool: ...

class TokenServicePort(ABC):
    @abstractmethod
    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str: ...
    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]: ...

class PersonalAccessTokenRepositoryPort(ABC):
    @abstractmethod
    def save(self, pat: PersonalAccessToken) -> None: ...
    @abstractmethod
    def get_by_hash(self, token_hash: TokenHash) -> PersonalAccessToken | None: ...
    @abstractmethod
    def list_by_user(self, user_id: UserId) -> list[PersonalAccessToken]: ...
    @abstractmethod
    def revoke(self, token_id: str, user_id: UserId) -> bool: ...
```

### 4.2 Use Cases

1. `RegisterUserUseCase`: Validates uniqueness of email, hashes password via `PasswordHasherPort`, persists new user.
2. `AuthenticateUserUseCase`: Verifies email and password, checks active status, generates short-lived JWT access token via `TokenServicePort`.
3. `CreatePersonalAccessTokenUseCase`: Generates cryptographically secure token, computes SHA-256 hash, stores metadata, and returns plaintext token to caller exactly once.
4. `ValidateTokenUseCase`: Decodes JWT, validates expiry and signature, returns `AuthenticatedUserDTO`.
5. `ValidatePersonalAccessTokenUseCase`: Hashes supplied token, checks lookup, expiry, and revocation, updates `last_used_at`, returns `AuthenticatedUserDTO`.

---

## 5. Infrastructure Layer (`src/identity/infrastructure/`)

1. **`Argon2PasswordHasherAdapter`**:
   - Implements `PasswordHasherPort` via `argon2-cffi`.
   - Invariant: `time_cost=3`, `memory_cost=65536`, `parallelism=4`.
2. **`JwtTokenServiceAdapter`**:
   - Implements `TokenServicePort` using PyJWT with configurable algorithm (HS256/RS256).
   - Invariant: Default expiry is 15 minutes. Includes `sub` (user_id), `email`, `roles`, `exp`, `iat`.
3. **`SqliteUserRepositoryAdapter` & `SqlitePatRepositoryAdapter`**:
   - Persists identities in SQLite WAL database (`cresmo_identity.db` or shared `cresmo_ledger.db`).
   - Prepared with clean SQL schemas and migration paths to PostgreSQL CloudNativePG.
4. **`IdentitySettings` (`pydantic-settings`)**:
   - Validates `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ARGON2_*` parameters with fail-fast validation.

---

## 6. Presentation Layer & BFF Integration

### 6.1 FastAPI Routes (`src/identity/presentation/routes.py`)

- `POST /api/v1/auth/register` $\rightarrow$ Register user.
- `POST /api/v1/auth/login` $\rightarrow$ Authenticate user, returns access token and user profile.
- `GET /api/v1/auth/me` $\rightarrow$ Returns current principal details.
- `POST /api/v1/auth/tokens` $\rightarrow$ Generates new PAT.
- `GET /api/v1/auth/tokens` $\rightarrow$ Lists active PATs for current user.
- `DELETE /api/v1/auth/tokens/{token_id}` $\rightarrow$ Revokes a PAT.

### 6.2 FastAPI Security Dependency (`dependencies.py`)

```python
async def get_current_user(...) -> AuthenticatedUserDTO:
    # 1. Inspect Authorization header for Bearer JWT
    # 2. Inspect X-Cresmo-PAT header for Personal Access Token
    # 3. Reject if neither is valid (HTTP 401)
```

### 6.3 SvelteKit BFF Workflow (`hooks.server.ts`)

1. User logs in through SvelteKit form action.
2. SvelteKit forwards request to FastAPI `/api/v1/auth/login`.
3. SvelteKit stores token in an `HttpOnly, Secure, SameSite=Strict` session cookie.
4. On subsequent page loads, `hooks.server.ts` resolves the cookie and attaches `Authorization: Bearer <token>` to all backend fetches.

---

## 7. Acceptance Criteria (TDD Test Suite)

- [ ] **Unit Tests (`tests/identity/unit/`)**:
  - `test_user_entity.py`: Validates user creation, invalid emails, active status invariants.
  - `test_argon2_hasher.py`: Verifies hashing, verification, and invalid password rejections.
  - `test_jwt_token_service.py`: Verifies token issuance, claims decoding, expiration handling.
  - `test_pat_use_cases.py`: Verifies creation, hashing, one-time reveal, and revocation.
- [ ] **Integration Tests (`tests/identity/integration/`)**:
  - `test_sqlite_repositories.py`: Verifies CRUD on SQLite WAL with concurrent write safety.
  - `test_auth_routes.py`: Verifies FastAPI routes and `get_current_user` dependency with both Bearer JWT and `X-Cresmo-PAT`.
