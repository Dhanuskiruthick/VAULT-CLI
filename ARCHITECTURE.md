# VAULT CLI - System Architecture

## Overview

VAULT CLI is a three-layer authentication system designed with security-first principles. Every architectural decision prioritizes defense over convenience.

## System Layers

### Layer 1: Input & Validation

```
┌─────────────────────────────┐
│   User Input (Terminal)     │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  Input Handler              │
│ • getpass for passwords     │
│ • sanitize usernames       │
│ • validate format          │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│  Validation Engine          │
│ • username: 3-20 chars     │
│ • no special chars         │
│ • password: 8+ chars       │
└──────────────┬──────────────┘
               ▼
        [Accept / Reject]
```

**Why this matters:**

- Prevents malformed input from reaching authentication layer
- Reduces attack surface early
- Clear error messages without leaking info

### Layer 2: Authentication & Cryptography

```
┌─────────────────────────────┐
│  Password Hashing Engine    │
│  (bcrypt with rounds=12)    │
└──────────────┬──────────────┘
               ▼
        ┌──────────┐
        │  bcrypt  │
        │ Hashing  │
        └──────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
[Registration]       [Authentication]
    │                     │
    └──────────┬──────────┘
               ▼
    [Store/Verify Hash]
```

**bcrypt Details:**

```
Input:  plaintext_password
        ↓
Algorithm: bcrypt
Cost Factor: 12 rounds (≈100ms per guess)
Output: $2b$12$SALT_AND_HASH_COMBINED
        ↓
Storage: password_hash column (never store plaintext)
```

**Why 12 rounds?**

```
Rounds  | Time per guess | Annual cost (single GPU)
6       | 4ms            | Crackable
8       | 50ms           | Risky
10      | 400ms          | Good
12      | 100ms          | Better (our choice)
14      | 1.6s           | Slow but secure
```

We chose 12 as the sweet spot between security and usability.

### Layer 3: Data Storage & Audit

```
┌──────────────────────────┐
│   SQLite Database        │
│   (vault.db)             │
└──────────────┬───────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────┐        ┌──────────────┐
│  Users   │        │ Audit Logger │
│  Table   │        │ (audit.log)  │
└──────────┘        └──────────────┘
```

**Users Table:**

```sql
id              INTEGER PRIMARY KEY  -- unique identifier
username        TEXT UNIQUE NOT NULL -- login name
password_hash   TEXT NOT NULL        -- bcrypt output
failed_attempts INTEGER DEFAULT 0    -- brute-force tracking
lock_until      INTEGER DEFAULT 0    -- timestamp lockout expires
created_at      TIMESTAMP           -- account creation time
```

**Why this schema?**

- Minimal columns (no unnecessary data = no unnecessary leaks)
- UNIQUE username prevents duplicate accounts
- failed_attempts enables lockout logic
- lock_until timestamp allows temporary lockouts
- No plaintext passwords anywhere

## Core Security Mechanisms

### 1. Password Hashing Flow

**Registration:**

```
user_password
    ↓
[Validate format]
    ↓
[Generate salt via bcrypt]
    ↓
[Hash password with salt]
    ↓
[Store hash in database]
    ↓
Never store plaintext
```

**Login:**

```
user_enters_password
    ↓
[Retrieve stored hash from database]
    ↓
[Use bcrypt.checkpw() to verify]
    ↓
[Constant-time comparison]
    ↓
[Grant/Deny access]
    ↓
Never compare plaintext strings
```

### 2. SQL Injection Prevention

**VULNERABLE PATTERN (Never use):**

```python
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)

# Attack: username = "admin'--"
# Query becomes: SELECT * FROM users WHERE username = 'admin'--'
# Result: Bypass successful!
```

**SECURE PATTERN (Always use):**

```python
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

# The database driver handles escaping
# No matter what username contains, it's treated as data, not code
# Attack impossible
```

**Why parameterized queries work:**

1. Database separates query structure from data
2. Special characters in data are automatically escaped
3. Attacker cannot inject SQL commands

### 3. Brute-Force Protection

**Logic Flow:**

```
Login attempt
    ↓
[Check if account is locked]
    ├─→ Is lock_until > current_time?
    │   ├─→ YES: Deny access, return error
    │   └─→ NO: Continue
    ▼
[Verify password]
    ├─→ Password correct?
    │   ├─→ YES: Reset failed_attempts to 0, grant access
    │   └─→ NO: Increment failed_attempts
    ▼
[Check lockout threshold]
    ├─→ failed_attempts >= 5?
    │   ├─→ YES: Set lock_until = current_time + 15 minutes
    │   └─→ NO: Allow next attempt
```

**Tradeoff:** Lockouts prevent brute-force but can be abused for DoS.

### 4. Secure Logging

**What We Log:**

```
✓ Login attempts (username only, no password)
✓ Failed authentication (reason, timestamp)
✓ Account lockouts (trigger event)
✓ Registration events (username, timestamp)
✓ Audit trail (who did what, when)
```

**What We Never Log:**

```
✗ Plaintext passwords
✗ Session tokens
✗ Cryptographic keys
✗ Personal data unnecessarily
✗ Internal system paths
```

**Log Format:**

```
[2024-01-15 14:32:45] LOGIN_SUCCESS - user: alice
[2024-01-15 14:33:12] LOGIN_FAILED - user: bob, reason: invalid_password
[2024-01-15 14:33:42] ACCOUNT_LOCKED - user: bob, duration: 15_minutes
[2024-01-15 14:40:00] LOGIN_SUCCESS - user: bob
```

## Data Flow Diagrams

### Registration Flow

```
START
  │
  ▼
┌──────────────────────┐
│ Get username         │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Validate username    │
│ (3-20 chars, no      │
│  special chars)      │
└──────────────────────┘
  │
  ├─→ Invalid? → [Show error] → END
  │
  ▼
┌──────────────────────┐
│ Check username       │
│ uniqueness in DB     │
└──────────────────────┘
  │
  ├─→ Exists? → [Show error] → END
  │
  ▼
┌──────────────────────┐
│ Get password         │
│ (hidden input)       │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Validate password    │
│ (8+ chars)           │
└──────────────────────┘
  │
  ├─→ Invalid? → [Show error] → END
  │
  ▼
┌──────────────────────┐
│ Get password confirm │
│ (hidden input)       │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Match passwords?     │
└──────────────────────┘
  │
  ├─→ No → [Show error] → END
  │
  ▼
┌──────────────────────┐
│ Hash password with   │
│ bcrypt (rounds=12)   │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Store in database    │
│ (username, hash)     │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Log registration     │
│ (secure logging)     │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Success message      │
└──────────────────────┘
  │
  ▼
END
```

### Authentication Flow

```
START
  │
  ▼
┌──────────────────────┐
│ Get username         │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Query database for   │
│ username             │
└──────────────────────┘
  │
  ├─→ Not found? → [Deny access] → END
  │
  ▼
┌──────────────────────┐
│ Check if account     │
│ is locked            │
└──────────────────────┘
  │
  ├─→ Locked? → [Show error] → END
  │
  ▼
┌──────────────────────┐
│ Get password         │
│ (hidden input)       │
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│ Use bcrypt.checkpw() │
│ to verify password   │
└──────────────────────┘
  │
  ├─→ Correct?
  │   │
  │   ├─→ YES: Reset failed_attempts → [Grant access] → END
  │   │
  │   └─→ NO: Increment failed_attempts
  │
  ▼
┌──────────────────────┐
│ failed_attempts >= 5?│
└──────────────────────┘
  │
  ├─→ YES: Set lock_until = now + 15min
  │        [Deny access] → END
  │
  └─→ NO: [Deny access] → END
```

## Security Decisions & Tradeoffs

| Decision | Benefit | Cost |
|----------|---------|------|
| bcrypt (slow hashing) | GPU-resistant | 100ms per login |
| Parameterized queries | SQL injection proof | Slight complexity |
| Account lockout | Brute-force resistant | Can be used for DoS |
| Secure logging | Prevent info leaks | Storage overhead |
| Password masking (getpass) | Shoulder surfing protection | Terminal-only |

## Attack Scenarios & Mitigations

### Scenario 1: Database Leak

**Attack:** Database is stolen. Attacker has all password hashes.

**Mitigation:**

- bcrypt cost factor 12 = 100ms per guess
- Cracking 1 password = hours on single GPU
- Cracking 1000 passwords = days with multiple GPUs
- Economics become unfavorable for attacker
- Stronger than SHA256 (instant cracking)

### Scenario 2: SQL Injection

**Attack:** `username = admin'--`

**Mitigation:**

- Parameterized queries separate code from data
- Database driver escapes all special characters
- Query structure cannot be altered
- Attack impossible

### Scenario 3: Brute-Force Login

**Attack:** Attacker tries 1000 password guesses rapidly

**Mitigation:**

- After 5 failed attempts, account locks for 15 minutes
- Lock is timestamp-based (temporary)
- Prevents rapid-fire guessing
- Real users can still recover

### Scenario 4: Log Leaks

**Attack:** Logs containing passwords are stolen

**Mitigation:**

- Passwords never logged
- Session tokens never logged
- Only login events and timestamps logged
- No sensitive data in logs
- Logging becomes safe to share

### Scenario 5: Timing Attack

**Potential Attack:** Measuring response time reveals if username exists

**Mitigation:**

- Always perform password check (even if user not found)
- Same response time whether user exists or not
- Attacker cannot enumerate valid usernames
- Timing remains constant

## Future Architecture Enhancements

### V2: Session Management

```
Login
  │
  ▼
Generate JWT token
  │
  ├─ Header: algorithm, type
  ├─ Payload: username, expiry, permissions
  └─ Signature: HMAC-SHA256
  │
  ▼
Store in secure HTTP-only cookie
  │
  ▼
Verify on each request
```

### V3: Multi-Factor Authentication

```
Login (password OK)
  │
  ▼
Generate TOTP challenge (Google Authenticator)
  │
  ▼
User scans QR code
  │
  ▼
User enters time-based code
  │
  ▼
Verify 6-digit code (valid for 30 seconds)
  │
  ▼
Grant access only if both factors verified
```

### V4: Encryption at Rest

```
User registers
  │
  ▼
bcrypt password
  │
  ▼
Create encryption key from master key
  │
  ▼
Encrypt sensitive user data
  │
  ▼
Store only ciphertext in database
  │
  ▼
Decrypt only when needed in memory
```

## Testing Architecture

```
Unit Tests
├─ Bcrypt hashing verification
├─ Password validation rules
├─ Input sanitization
└─ Database queries

Integration Tests
├─ Full registration flow
├─ Full authentication flow
├─ Lockout mechanism
└─ Logging functionality

Security Tests
├─ SQL injection attempts
├─ XSS prevention (if web version)
├─ Timing attack resistance
└─ Brute-force rate limiting
```

## Performance Considerations

**Current:**

```
Registration: ~100ms (bcrypt cost factor 12)
Login attempt: ~100ms (bcrypt cost factor 12)
Database query: ~1ms
Logging: ~2ms
Total per login: ~103ms
```

**Scaling:**

- Single user: instant
- 1000 users: no impact
- 100k concurrent users: add connection pooling
- 1M+ users: migrate to production auth system

**Optimization opportunities:**

- Add Redis for session caching
- Implement connection pooling for database
- Use async/await for I/O operations
- Add request queuing for high load

## Deployment Architecture (Future)

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  HTTPS      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Load      │
│  Balancer   │
└──────┬──────┘
       │
    ┌──┴──┐
    ▼     ▼
  ┌──┐  ┌──┐
  │App├──┤App│  (Multiple instances)
  └──┴──┴──┘
    │
    ▼
┌──────────────────┐
│  PostgreSQL DB   │  (Replicated)
└──────────────────┘
    │
    ▼
┌──────────────────┐
│  Audit Logging   │  (Separate server)
└──────────────────┘
    │
    ▼
┌──────────────────┐
│  SIEM System     │  (Security monitoring)
└──────────────────┘
```

---

**This architecture prioritizes security without sacrificing usability. Every layer has a clear purpose in the defense strategy.**
