# VAULT CLI 🔐

> A secure authentication system built to understand real security engineering

A terminal-based secure authentication system that teaches cybersecurity fundamentals through actual implementation, not just theory.

## What is VAULT CLI?

Most cybersecurity learning stays stuck in videos and certifications. VAULT CLI is different — it's a complete authentication system built from scratch to answer the question:

**"How do real security engineers think?"**

Instead of just studying authentication, I built one and discovered why every decision matters.

## Key Features

✅ **Secure User Registration & Login**  
✅ **bcrypt Password Hashing** — slow, expensive, GPU-resistant  
✅ **SQLite Database** — minimal schema, maximum security  
✅ **Brute-Force Protection** — failed login tracking + account lockouts  
✅ **SQL Injection Prevention** — parameterized queries throughout  
✅ **Secure Audit Logging** — no passwords, no secrets in logs  
✅ **Password Masking** — using `getpass` module  
✅ **Secure Input Handling** — validation at every layer  

## Why This Project Matters

A beginner thinks: *"Login = username + password"*

A security engineer thinks:

- What if the database leaks?
- What if attackers have GPU farms for cracking?
- What if logs contain passwords?
- What if timing differences leak secrets?
- What if lockout logic enables DoS attacks?
- What if SQL injection bypasses authentication?

This project forces that mindset shift.

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/vault-cli.git
cd vault-cli

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Run the application
python vault_cli.py

# Follow the prompts for registration or login
```

### Example Session

```
=== VAULT CLI ===
1. Register
2. Login
3. Exit

Choose: 1

Enter username: alice
Enter password: (hidden input)
Confirm password: (hidden input)

✓ Registration successful!

=== VAULT CLI ===
1. Register
2. Login
3. Exit

Choose: 2

Enter username: alice
Enter password: (hidden input)

✓ Login successful!
```

## Core Security Lessons

### 1. Why bcrypt > SHA256

**The Problem with Fast Hashes:**

SHA256 is cryptographically strong but dangerously fast. In a database leak:

```
Attackers can run billions of guesses
GPU parallel cracking
Dictionary attacks
Rule-based mutations
All extremely cheaply
```

**bcrypt's Solution:**

```python
# bcrypt is intentionally slow and expensive
import bcrypt

password = b"secure_password"
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
# Each guess now costs ~100ms of computation
# At scale: economically painful
```

**Result:** Every password guess costs attackers more time, electricity, and money.

### 2. bcrypt's Hidden Genius

I thought salt and hash had to be stored separately. Wrong.

bcrypt stores everything in one string:

```
$2b$12$PSZ6DiipoQ/wJAkJaW6yEOG74ITTE/ZPRKiF8HEn/6Gz0B6zo3qS6

$2b$   → bcrypt version
12     → cost factor (work factor)
rest   → salt + hash embedded internally
```

This single decision simplified the entire database design.

### 3. SQL Injection: Thinking Like an Attacker

This string looks random: `admin'--`

It's actually an SQL injection attempt:

```python
# VULNERABLE (Never do this!)
query = "SELECT * FROM users WHERE username = '" + username + "'"
# If username = admin'--
# Query becomes: SELECT * FROM users WHERE username = 'admin'--'
# The -- comments out the password check!

# SECURE (Always do this!)
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
# Database handles escaping, injection impossible
```

### 4. Logs: The Forgotten Attack Surface

Logs can leak secrets. Things that should NEVER be logged:

```python
❌ Plaintext passwords
❌ Session tokens
❌ Cryptographic keys
❌ Personal data unnecessarily

# Instead, log securely:
✓ Login attempts (without passwords)
✓ Lockout events
✓ Failed authentications (without sensitive data)
```

### 5. Security Tradeoffs

Every defense has costs:

**Account Lockout** stops brute-force but enables DoS attacks on real users.

**Secure Logging** helps debugging but costs storage and access time.

**Strong Password Requirements** improve security but reduce usability.

Real security engineering = balancing these tradeoffs, not chasing "perfect protection."

## Architecture

```
┌──────────────────┐
│   User Terminal  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Input Layer     │
│ (getpass/input)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Validation Layer │
│ username checks  │
│ password rules   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Authentication   │
│ bcrypt hashing   │
│ password verify  │
└────────┬─────────┘
         │
    ┌────┴──────┐
    ▼           ▼
┌─────────┐ ┌────────────┐
│ SQLite  │ │ Audit Log  │
│ Database│ │ (secure)   │
└─────────┘ └────────────┘
```

**See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed diagrams and system design.**

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    failed_attempts INTEGER DEFAULT 0,
    lock_until INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Design Philosophy:**

- Store only what you truly need
- Never store plaintext passwords
- bcrypt hash includes salt and work factor
- Track failed attempts for lockout protection
- Timestamp for audit trails

## File Structure

```
vault-cli/
├── vault_cli.py           # Main application
├── requirements.txt       # Python dependencies
├── vault.db              # SQLite database (created on first run)
├── audit.log             # Secure audit logging
├── docs/
│   ├── ARCHITECTURE.md   # Detailed system design
│   ├── SECURITY.md       # Security design decisions
│   └── ROADMAP.md        # Future features & upgrades
├── README.md             # This file
└── LICENSE               # MIT License
```

## Dependencies

```
bcrypt==4.0.1          # Password hashing
```

See `requirements.txt` for complete list.

## Security Considerations

### ✅ What This Project Does Right

1. **Parameterized Queries** - SQL injection protection
2. **Slow Hashing** - bcrypt with appropriate cost factor
3. **Input Validation** - username and password checks
4. **Secure Logging** - no sensitive data in logs
5. **Lockout Protection** - brute-force mitigation
6. **Password Masking** - hidden input via getpass

### ⚠️ What This Project Doesn't Cover

This is V1, built for learning. For production use, add:

- [ ] Multi-factor authentication (TOTP/SMS)
- [ ] Session management with JWT tokens
- [ ] Password reset via email verification
- [ ] Rate limiting on API endpoints
- [ ] HTTPS/TLS encryption
- [ ] Secrets management (environment variables)
- [ ] Cryptographic key rotation
- [ ] Intrusion detection systems

See [ROADMAP.md](./docs/ROADMAP.md) for future plans.

## Running Tests

```bash
# Run security audit
python -m pytest tests/

# Check bcrypt functionality
python -c "import bcrypt; print('bcrypt OK')"

# Verify SQL injection protection
python vault_cli.py  # Try: admin'-- (will fail, as expected)
```

## Learning Goals

This project was built to understand:

- ✅ How authentication systems work
- ✅ Why certain cryptographic choices matter
- ✅ How attackers think about systems
- ✅ Security engineering tradeoffs
- ✅ Defensive thinking vs offensive thinking

## Project Stats

- **Built by:** A first-year cybersecurity student
- **Lines of Code:** ~300 (intentionally minimal, not bloated)
- **Security Concepts Learned:** 15+
- **Coffee Cups:** Too many
- **Times I Thought "Oh No":** 8

## What's Next (V2 Roadmap)

```
🔄 In Progress
├── Password policy engine
├── Session management (JWT)
└── Audit log encryption

📋 Planned
├── Multi-factor authentication (TOTP)
├── Encrypted credential vault
├── Role-based access control
├── REST API version
├── Docker containerization
└── Rate limiting middleware
```

## How to Contribute

Found a security issue? Awesome!

1. **Security Vulnerabilities:** Email me directly (don't open a public issue)
2. **Bug Reports:** Open an issue with reproduction steps
3. **Features:** Open an issue to discuss before submitting PR
4. **Improvements:** Submit a PR with clear explanation

### Development Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/vault-cli.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python vault_cli.py
```

## Learning Resources Referenced

While building this project, I learned from:

- **Password Hashing:** OWASP Authentication Cheat Sheet
- **SQL Injection:** PortSwigger Web Security Academy
- **Cryptography:** Stanford CS255 (free online)
- **Threat Modeling:** Microsoft Secure Development Lifecycle
- **Secure Logging:** SANS Institute Security Resources

## The Biggest Lesson

> "The fastest way to learn cybersecurity isn't endless theory.
> It's: Learn → Build → Break → Fix → Repeat"

This project taught me more about security in one month of building than six months of passive studying.

## Author

**Dhanus Kiruthick**  
First-year Integrated MTech (Cybersecurity)  
VIT Bhopal University

Building security tools. Learning by breaking things. Coffee-fueled.

## License

MIT License - See [LICENSE](./LICENSE) file for details

## Disclaimer

This project is for educational purposes. It demonstrates security concepts but shouldn't be used in production without significant hardening.

For production authentication, use established frameworks:
- Django (Python web framework)
- FastAPI with OAuth2
- AWS Cognito
- Auth0

## Show Your Support

If this helped you learn something about security engineering:

⭐ Star this repo  
🔗 Share it with other students  
📝 Write about what you learned  

Let's build more secure systems together. 🔐

---

**Questions?** Open an issue or reach out. I love talking about security engineering!
