# 🏗️ VAULT CLI — System Architecture Document

**Project**: VAULT CLI - Educational Authentication System  
**Version**: 1.0  
**Author**:dhanus kiruthick / First-Year Student / Security Learner  
**Last Updated**: 2026  

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Layers](#architectural-layers)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Database Schema](#database-schema)
7. [Module Interactions](#module-interactions)
8. [Performance Characteristics](#performance-characteristics)
9. [Security Considerations](#security-considerations)
10. [Design Decisions](#design-decisions)

---

## System Overview

### Purpose
VAULT CLI is an educational authentication system designed to demonstrate secure password management, authentication flow, and security mechanisms through practical implementation.

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    CLI INTERFACE (main.py)                │
│              (User input, menu navigation)                │
└────────────────┬──────────────────────────┬───────────────┘
                 │                          │
     ┌───────────▼─────────┐    ┌──────────▼────────────┐
     │ REGISTRATION MODULE │    │  LOGIN MODULE         │
     │   (register.py)     │    │  (login.py)           │
     └───────────┬─────────┘    └──────────┬────────────┘
                 │                          │
                 └───────────┬──────────────┘
                             │
                ┌────────────▼────────────┐
                │  AUTHENTICATION LAYER   │
                │  (bcrypt hashing)       │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │  DATABASE LAYER         │
                │  (SQLite)               │
                │  - Users table          │
                │  - Failed attempts      │
                │  - Lockout state        │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │  SECURITY STATE MGR     │
                │  - Lockout tracking     │
                │  - Attempt counting     │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │  AUDIT LOGGER           │
                │  (logger.py)            │
                │  → audit.log            │
                └─────────────────────────┘
```

---

## Architectural Layers

### Layer 1: Presentation Layer (CLI)
**File**: `main.py`

**Responsibility**: User interaction and menu navigation

**Components**:
```python
Menu system:
  - Register option
  - Login option
  - Exit option

Input handling:
  - Username input
  - Password input (masked)
  - Menu selection

Output handling:
  - Success/failure messages
  - Error prompts
  - Menu display
```

**Key Features**:
- Menu-driven interface
- Input validation at CLI level
- User-friendly error messages
- Clear navigation flow

---

### Layer 2: Application Logic Layer
**Files**: `register.py`, `login.py`

#### Registration Module (`register.py`)

**Responsibility**: Handle new user registration

**Process Flow**:
```
1. Receive username & password from CLI
2. Validate inputs:
   - Username length (min 3 chars)
   - Password length (min 6 chars)
   - Username uniqueness
3. Hash password with bcrypt
4. Store in database
5. Log registration event
```

**Key Functions**:
```python
def validate_username(username):
    # Check length, special chars, uniqueness
    
def validate_password(password):
    # Check length, complexity
    
def register_user(username, password):
    # Hash with bcrypt
    # Insert into database
    # Log event
```

#### Login Module (`login.py`)

**Responsibility**: Handle user authentication

**Process Flow**:
```
1. Receive username & password
2. Check if account is locked
3. If locked, check lock expiry
4. Query database for user
5. If user exists:
   a. Compare passwords with bcrypt
   b. If match → Login success
   c. If no match → Increment failed attempts
6. If 3 failed attempts → Lock account
7. Log result
```

**Key Functions**:
```python
def authenticate_user(username, password):
    # Verify password with bcrypt.checkpw()
    
def check_lockout(username):
    # Check if account locked and if lock expired
    
def increment_failed_attempts(username):
    # Track failed login attempts
    
def lock_account(username):
    # Set lockout flag and timestamp
```

---

### Layer 3: Authentication Layer
**Integrated in** `login.py` and `register.py`

**Responsibility**: Cryptographic operations

**Technology**: bcrypt

**Key Concepts**:

1. **Password Hashing Process** (Registration)
```
Plain Password: "MySecure!Pass"
                    ↓
         bcrypt.hashpw(password, salt)
                    ↓
Hashed: $2b$12$vFjXKR9.sJvGTw9h5XAWSeV.X0LxZx5...
        (128-bit salt + cost factor embedded)
                    ↓
      Stored in database
```

2. **Password Verification** (Login)
```
Entered Password: "MySecure!Pass"
Stored Hash: $2b$12$vFjXKR9.sJvGTw9h5XAWSeV...
                    ↓
         bcrypt.checkpw(entered, stored)
                    ↓
            Returns True/False
```

3. **Cost Factor**
```python
# Cost = 12 (default)
# ~50 hashes/second on modern hardware
# Prevents brute-force attacks

bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
```

---

### Layer 4: Database Layer
**File**: `database.py`

**Responsibility**: Data persistence and retrieval

**Technology**: SQLite3

**Database Structure**:

```sqlite
TABLE: users
├── id (INTEGER PRIMARY KEY)
├── username (TEXT UNIQUE)
├── password_hash (TEXT)
├── created_at (TIMESTAMP)
├── is_locked (BOOLEAN)
├── locked_until (TIMESTAMP)
└── failed_attempts (INTEGER)
```

**Key Operations**:

```python
def create_connection():
    # Establish SQLite connection
    # Create schema if needed
    
def insert_user(username, password_hash):
    # Parameterized query (SQL injection prevention)
    INSERT INTO users (username, password_hash, created_at)
    
def get_user(username):
    # Retrieve user record for authentication
    
def update_failed_attempts(username):
    # Increment failed attempts counter
    
def lock_account(username, lock_duration):
    # Set is_locked=True, locked_until=timestamp
    
def unlock_account(username):
    # Set is_locked=False, failed_attempts=0
```

**Security Features**:
- Parameterized queries (prevent SQL injection)
- No plaintext password storage
- Timestamp-based lockout tracking

---

### Layer 5: Security State Management
**Integrated in** `login.py`, `database.py`

**Responsibility**: Track authentication state

**State Variables**:
```python
{
    username: str,
    failed_attempts: int,
    is_locked: bool,
    locked_until: timestamp,
    last_login: timestamp
}
```

**Lockout Mechanism**:

```
Failed Attempts:
  1 → Warning message
  2 → Warning message
  3 → Account locked for 15 minutes

Unlock Triggers:
  - Time expires (15 min)
  - Manual unlock (admin only, not implemented)
  
On unlock:
  - Reset failed_attempts to 0
  - Set is_locked to False
```

---

### Layer 6: Audit Logging Layer
**File**: `logger.py`

**Responsibility**: Security event tracking

**Log Format**:
```
TIMESTAMP | EVENT_TYPE | USERNAME | DETAILS
2024-01-15 14:23:45 | LOGIN_SUCCESS | alice | Authentication successful
2024-01-15 14:24:12 | LOGIN_FAILED | bob | Invalid credentials
2024-01-15 14:24:18 | ACCOUNT_LOCKED | bob | Exceeded max attempts
```

**Event Types**:
| Event | Severity | Logged Details |
|-------|----------|----------------|
| REGISTRATION | INFO | username, timestamp |
| LOGIN_SUCCESS | INFO | username, timestamp |
| LOGIN_FAILED | WARNING | username, attempt #, timestamp |
| ACCOUNT_LOCKED | WARNING | username, lock duration, timestamp |
| ACCOUNT_UNLOCKED | INFO | username, timestamp |

**Key Features**:
- Structured logging
- Timestamps for all events
- Never logs passwords or hashes
- Append-only design

---

## Component Design

### Component 1: Main CLI (`main.py`)

```python
class VaultCLI:
    def __init__(self):
        self.db = Database()
        self.logger = Logger()
    
    def main_menu(self):
        """Display menu and handle user choice"""
        while True:
            print("\n🔐 VAULT CLI")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Select: ")
            
            if choice == "1":
                self.register_flow()
            elif choice == "2":
                self.login_flow()
            elif choice == "3":
                break
    
    def register_flow(self):
        """Handle registration process"""
        # Get username
        # Get password (masked)
        # Validate
        # Store securely
    
    def login_flow(self):
        """Handle login process"""
        # Get username
        # Get password (masked)
        # Authenticate
        # Log result
```

**Diagram**:
```
┌─────────────────────────┐
│   Display Main Menu     │
└────────┬────────────────┘
         │
    ┌────┴────┬────────┐
    │          │        │
    ▼          ▼        ▼
 Register    Login     Exit
    │          │
    └──────┬───┘
           ▼
      Log Event
           │
           ▼
      Return to Menu
```

### Component 2: Registration (`register.py`)

```python
class RegistrationManager:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
    
    def validate_input(self, username, password):
        """Validate username and password"""
        # Check username length ≥ 3
        # Check password length ≥ 6
        # Check username not taken
        return True/False
    
    def hash_password(self, password):
        """Hash with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt)
    
    def register(self, username, password):
        """Create new user"""
        if not self.validate_input(username, password):
            return False
        
        hash = self.hash_password(password)
        self.db.insert_user(username, hash)
        self.logger.log("REGISTRATION", username)
        return True
```

### Component 3: Login (`login.py`)

```python
class LoginManager:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self.max_attempts = 3
        self.lockout_duration = 900  # seconds
    
    def check_lockout(self, username):
        """Check if account is locked"""
        user = self.db.get_user(username)
        if not user or not user['is_locked']:
            return False
        
        # Check if lock expired
        if time.time() > user['locked_until']:
            self.db.unlock_account(username)
            return False
        
        return True
    
    def verify_password(self, entered_pwd, stored_hash):
        """Verify password with bcrypt"""
        return bcrypt.checkpw(
            entered_pwd.encode(),
            stored_hash.encode()
        )
    
    def authenticate(self, username, password):
        """Main authentication logic"""
        # Check if locked
        if self.check_lockout(username):
            self.logger.log("LOGIN_FAILED", username, "Account locked")
            return False
        
        # Get user
        user = self.db.get_user(username)
        if not user:
            self.logger.log("LOGIN_FAILED", username, "User not found")
            return False
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            # Increment attempts
            self.db.increment_failed_attempts(username)
            
            if user['failed_attempts'] + 1 >= self.max_attempts:
                self.db.lock_account(
                    username,
                    self.lockout_duration
                )
                self.logger.log("ACCOUNT_LOCKED", username)
            else:
                self.logger.log("LOGIN_FAILED", username)
            
            return False
        
        # Success
        self.db.reset_failed_attempts(username)
        self.logger.log("LOGIN_SUCCESS", username)
        return True
```

### Component 4: Database (`database.py`)

```python
class Database:
    def __init__(self, db_path='vault.db'):
        self.db_path = db_path
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database and create schema"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Create users table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_locked BOOLEAN DEFAULT 0,
                locked_until TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def insert_user(self, username, password_hash):
        """Insert new user (parameterized query)"""
        self.conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash.decode())
        )
        self.conn.commit()
    
    def get_user(self, username):
        """Retrieve user by username"""
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()
```

### Component 5: Logger (`logger.py`)

```python
class AuditLogger:
    def __init__(self, log_file='audit.log'):
        self.log_file = log_file
    
    def log(self, event_type, username, details=""):
        """Log security event"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp} | {event_type} | {username} | {details}"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def read_logs(self):
        """Read and display audit trail"""
        with open(self.log_file, 'r') as f:
            return f.readlines()
```

### Component 6: Attack Simulator (`cracker.py`)

```python
class DictionaryAttacker:
    def __init__(self, dictionary_file):
        self.dictionary = self.load_dictionary(dictionary_file)
    
    def load_dictionary(self, filepath):
        """Load common passwords"""
        with open(filepath) as f:
            return [line.strip() for line in f]
    
    def crack_password(self, password_hash):
        """Try dictionary attack"""
        for password in self.dictionary:
            if bcrypt.checkpw(
                password.encode(),
                password_hash.encode()
            ):
                return password
        return None
    
    def attack_database(self, db):
        """Crack all passwords in database"""
        users = db.get_all_users()
        
        for user in users:
            cracked = self.crack_password(user['password_hash'])
            
            if cracked:
                print(f"✓ {user['username']}: {cracked}")
            else:
                print(f"✗ {user['username']}: NOT CRACKED")
```

---

## Data Flow

### Registration Flow

```
User Input
   │ "register"
   ▼
┌─────────────────┐
│ Get Username    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Get Password    │
│ (masked input)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Validate Input          │
│ - Length checks         │
│ - Username uniqueness   │
└────────┬────────────────┘
         │
    ┌────▼────┐
    │ Valid?  │
    └┬───────┬┘
     │       │
    NO      YES
     │       │
     │       ▼
     │    ┌──────────────────┐
     │    │ Hash Password    │
     │    │ bcrypt (cost=12) │
     │    └────────┬─────────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ Insert to DB     │
     │    │ (parameterized)  │
     │    └────────┬─────────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ Log Registration │
     │    │ audit.log        │
     │    └────────┬─────────┘
     │             │
     ▼             ▼
  Error      Success Message
  Message    
```

### Authentication Flow

```
User Input
   │ username + password
   ▼
┌────────────────────┐
│ Get Username       │
│ Get Password       │
│ (masked)           │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Check Account      │
│ Lockout Status     │
└────────┬───────────┘
         │
    ┌────▼─────┐
    │ Locked?  │
    └┬────────┬┘
     │        │
    YES      NO
     │        │
     │        ▼
     │    ┌────────────────────┐
     │    │ Query Database     │
     │    │ Find User Record   │
     │    └────────┬───────────┘
     │             │
     │        ┌────▼─────┐
     │        │ Found?   │
     │        └┬────────┬┘
     │         │        │
     │         NO      YES
     │         │        │
     │         │        ▼
     │         │    ┌────────────────────┐
     │         │    │ bcrypt.checkpw()   │
     │         │    │ Verify Password    │
     │         │    └────────┬───────────┘
     │         │             │
     │         │        ┌────▼────┐
     │         │        │ Match?  │
     │         │        └┬───────┬┘
     │         │         │       │
     │         │        YES     NO
     │         │         │       │
     │         │         │       ▼
     │         │         │   ┌─────────────────┐
     │         │         │   │ Increment       │
     │         │         │   │ Failed Attempts │
     │         │         │   └────────┬────────┘
     │         │         │            │
     │         │         │        ┌───▼────┐
     │         │         │        │ ≥3     │
     │         │         │        │ times? │
     │         │         │        └┬──────┬┘
     │         │         │         │      │
     │         │         │        YES    NO
     │         │         │         │      │
     │         │         │         ▼      ▼
     │         │         │    Lock Acc. Failed Msg
     │         │         │         │
     │         │         └─────┬───┘
     │         │               │
     │         └───────┬───────┘
     │                 │
     │                 ▼
     │         ┌────────────────┐
     │         │ Log Event      │
     │         │ audit.log      │
     │         └────────┬───────┘
     │                  │
     ▼                  ▼
  Locked          Error Message
  Message         
                  OR
                  
                  Success +
                  Welcome Message
```

---

## Security Architecture

### Password Security Model

```
┌──────────────────────────────────────┐
│  INPUT LAYER                         │
│  User enters password "MyP@ssw0rd"   │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│  MASKING LAYER                       │
│  Display: ••••••••••                 │
│  Prevents shoulder surfing           │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│  ENCODING LAYER                      │
│  Convert to bytes: b'MyP@ssw0rd'     │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│  HASHING LAYER (bcrypt)              │
│  - Generate random salt              │
│  - Hash with cost factor 12          │
│  - Output: $2b$12$...256bits...      │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│  STORAGE LAYER                       │
│  Store hash only in database         │
│  Original password never stored      │
└──────────────────────────────────────┘
```

### Authentication Security Model

```
LOGIN ATTEMPT:

Input: "MyP@ssw0rd"
Stored: $2b$12$...hash...

                ↓
         bcrypt.checkpw()
                ↓
        Hash input with same salt
                ↓
        Compare to stored hash
                ↓
         Match? YES/NO
```

### Brute-Force Protection

```
ATTEMPT 1 (Time: 0:00)
├─ Try password
├─ FAIL
└─ failed_attempts = 1

ATTEMPT 2 (Time: 0:05)
├─ Try different password
├─ FAIL
└─ failed_attempts = 2

ATTEMPT 3 (Time: 0:10)
├─ Try another password
├─ FAIL
└─ failed_attempts = 3 → ACCOUNT LOCKED

ATTEMPTS 4+ (Time: 0:15)
├─ Try more passwords
├─ BLOCKED - Account locked
└─ Lock expires at 0:25 (15 minutes)

AFTER LOCK EXPIRES (Time: 0:26)
├─ User can try again
├─ failed_attempts reset to 0
└─ Normal login process resumes
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    username TEXT UNIQUE NOT NULL,
    -- Unique identifier for user
    
    password_hash TEXT NOT NULL,
    -- Bcrypt hash (never plaintext)
    -- Format: $2b$12$[22 char salt][31 char hash]
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Account creation time
    
    is_locked BOOLEAN DEFAULT 0,
    -- Lock status: 0=unlocked, 1=locked
    
    locked_until TIMESTAMP,
    -- When lock expires (NULL if not locked)
    
    failed_attempts INTEGER DEFAULT 0
    -- Count of consecutive failed logins
);
```

### Example Records

```sql
-- User with strong password (not crackable)
INSERT INTO users VALUES (
    1,
    'alice',
    '$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqQuzi.Hy.W/VZl.EAcFjq',
    '2024-01-15 10:30:00',
    0,
    NULL,
    0
);

-- User with weak password (easily crackable)
INSERT INTO users VALUES (
    2,
    'bob',
    '$2b$12$vFjXKR9.sJvGTw9h5XAWSeV.X0LxZx5n7bE...',
    '2024-01-15 10:35:00',
    1,
    '2024-01-15 10:50:00',
    3
);
```

---

## Module Interactions

### Interaction Diagram

```
┌─────────────────┐
│   main.py       │
│  (CLI Entry)    │
└────┬────────┬───┘
     │        │
     │        └──────────────┐
     │                       │
     ▼                       ▼
┌──────────┐         ┌───────────┐
│register  │         │ login.py  │
│.py       │         │           │
└────┬─────┘         └─────┬─────┘
     │                     │
     │                     │
     └──────────┬──────────┘
                │
     ┌──────────▼──────────┐
     │  Authentication     │
     │  (bcrypt layer)     │
     └──────────┬──────────┘
                │
     ┌──────────▼──────────┐
     │  database.py        │
     │  (SQLite queries)   │
     └──────────┬──────────┘
                │
     ┌──────────▼──────────┐
     │  logger.py          │
     │  (Audit logging)    │
     └─────────────────────┘
```

### Interaction Example: Login Flow

```python
# 1. main.py calls login module
login_manager = LoginManager(db, logger)

# 2. login.py uses database layer
user = database.get_user("alice")

# 3. database.py executes SQL
cursor.execute("SELECT * FROM users WHERE username = ?", ("alice",))

# 4. login.py uses bcrypt (authentication layer)
bcrypt.checkpw(entered_password, user['password_hash'])

# 5. login.py uses logger
logger.log("LOGIN_SUCCESS", "alice")

# 6. logger.py writes to audit.log
f.write("2024-01-15 14:23:45 | LOGIN_SUCCESS | alice\n")
```

---

## Performance Characteristics

### Hashing Performance

| Operation | Time | Relative Speed |
|-----------|------|-----------------|
| SHA256 hash | 0.00001s | 1x |
| bcrypt (cost=10) | 0.001s | 100x slower |
| bcrypt (cost=12) | 0.02s | 2,000x slower |
| bcrypt (cost=14) | 0.2s | 20,000x slower |

### Database Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Insert user | ~5ms | Includes bcrypt hashing |
| Query user | ~1ms | Indexed on username |
| Update attempts | ~2ms | Quick state change |
| Lock account | ~2ms | Write timestamp |

### Overall Login Time

```
Average login (success): ~50-100ms
├─ Password input: ~0ms
├─ Database query: ~1ms
├─ bcrypt verification: ~20ms (cost=12)
├─ Logging: ~2ms
└─ UI response: variable

Lockout check: ~1ms
Failed login: ~30ms total
```

---

## Security Considerations

### What This System Protects Against

| Threat | Protection | Mechanism |
|--------|-----------|-----------|
| Plaintext storage | ✅ | bcrypt hashing |
| Dictionary attacks | ✅ | bcrypt slowness |
| Brute-force attacks | ✅ | Account lockout |
| SQL injection | ✅ | Parameterized queries |
| Credential theft | ✅ | Password masking |
| Unauthorized access | ✅ | Password verification |
| Attack detection | ✅ | Audit logging |

### What This System Does NOT Protect Against

| Threat | Reason |
|--------|--------|
| Network interception | No TLS/HTTPS |
| Database theft | Unencrypted database file |
| Session hijacking | No session tokens |
| Man-in-the-middle | No encryption |
| Malware on client | Can't protect local machine |
| Denial-of-service | Simple lockout is exploitable |
| Insider threats | No role-based access |

### Security Hardening (Future)

```python
# 1. Add password complexity requirements
if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*]).{8,}$", password):
    raise PasswordTooWeak()

# 2. Add rate limiting
@rate_limit(5, 60)  # 5 attempts per minute
def login(username, password):
    pass

# 3. Add session tokens
session_token = secrets.token_hex(32)
sessions[username] = {
    'token': session_token,
    'created': time.time(),
    'expires': time.time() + 3600
}

# 4. Add 2FA
if user['2fa_enabled']:
    send_otp_to_email(user['email'])
    require_otp_validation()

# 5. Encrypt audit logs
encrypted_log = encrypt_log_entry(log_entry, encryption_key)

# 6. Add account recovery
send_recovery_email_with_temp_token(username)
```

---

## Design Decisions

### 1. Why bcrypt Instead of SHA256?

**Decision**: Use bcrypt for password hashing

**Rationale**:
- SHA256: 100,000 hashes/second → Fast for attacks
- bcrypt: 50 hashes/second → Slow for attacks
- bcrypt has built-in salt
- Cost factor allows future adjustments

**Trade-off**: Slower login (~20ms) vs. much more secure

### 2. Why SQLite Instead of PostgreSQL?

**Decision**: Use SQLite for simplicity

**Rationale**:
- Educational project, no server needed
- Zero setup, single file database
- Sufficient for demonstrating concepts
- No external dependencies

**Limitation**: Not suitable for production multi-user systems

### 3. Why Account Lockout?

**Decision**: Lock account after 3 failed attempts

**Rationale**:
- Stops brute-force attacks
- Clear feedback to users
- Automatic unlock after 15 minutes

**Trade-off**: Vulnerable to DoS attacks (lock legitimate users)

### 4. Why Audit Logging?

**Decision**: Log all security events

**Rationale**:
- Can't defend against what you can't see
- Helps understand attack patterns
- Educational value for learner
- Shows security mindset

### 5. Why Attack Simulator?

**Decision**: Include cracker.py for learning

**Rationale**:
- Understand how attackers actually work
- See impact of weak passwords
- Build defensive thinking
- Safe environment to experiment

### 6. Why No Session Management?

**Decision**: Keep simple for educational purposes

**Rationale**:
- Focus on authentication, not sessions
- Simplifies learning path
- Real systems would use JWT/OAuth

**Future**: Add session tokens for completeness

---

## Deployment Considerations

### Development Environment
```
Python 3.7+
Dependencies: bcrypt==4.0.1
Location: Single directory
Database: vault.db (local file)
Logs: audit.log (local file)
```

### Local Testing
```bash
python main.py          # Start application
python speed_test.py    # Test hashing speed
python cracker.py       # Test attack simulation
```

### Not Recommended For
- ❌ Production systems
- ❌ Real user data
- ❌ Public internet deployment
- ❌ Multi-user concurrent access
- ❌ High-security environments

---

## Conclusion

VAULT CLI demonstrates core authentication security concepts through practical implementation. While not production-ready, it provides valuable learning about:

- Secure password hashing
- Authentication flow
- Security trade-offs
- Attack simulation
- Audit logging
- System architecture

The educational value comes from **building and understanding** rather than copy-pasting production code.

---

**For Questions or Improvements**: See GitHub Issues

**For Learning More**: Read the Medium blog post and inline code comments
