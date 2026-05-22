# 🔐 VAULT CLI — A Learning Journey Through Authentication Security

> A Python-based authentication system built to understand real-world security engineering through practical implementation. This is an educational project designed to teach, not a production-ready system.

<img width="760" height="501" alt="image" src="https://github.com/user-attachments/assets/b9f60464-1015-412e-9b2c-b1b0b2d12c1a" />


## 📌 Project Overview

VAULT CLI is a terminal-based authentication system that demonstrates how password security actually works. Instead of memorizing that "bcrypt is better," you can *see why* through practical implementation.

**Purpose**: Educational security engineering through hands-on building.

**Built by**: A first-year student who got tired of theory.

---

## ✨ Features

### 🔐 Core Authentication
- **User Registration** — Validation, password strength checks, secure storage
- **Secure Login** — Password masking, bcrypt verification, session awareness
- **Password Hashing** — Industry-standard bcrypt, no plaintext storage
- **Account Management** — User data persistence with SQLite

### 🧠 Security Mechanisms
- **Failed Attempt Tracking** — Monitor login failures in real-time
- **Account Lockout** — Auto-lock after 3 failed attempts (15-minute duration)
- **Time-Based Release** — Automatic account unlock after lockout period
- **Session Management** — Track login state and user context

### 🗄️ Database Layer
- **SQLite Database** — Lightweight, no external dependencies
- **Parameterized Queries** — Protection against SQL injection
- **Persistent Storage** — Credentials survive application restart
- **Schema Management** — Automatic table creation on startup

### 📊 Security Logging & Monitoring
- **Audit Logging** — Every security event is recorded
- **Event Types Tracked**:
  - `LOGIN_SUCCESS` — Successful authentication
  - `LOGIN_FAILED` — Failed login attempt
  - `ACCOUNT_LOCKED` — Lockout triggered
  - `REGISTRATION` — New user created
- **Audit Trail** — Timestamped logs for forensic analysis

### ⚔️ Attack Simulation (Educational Lab)
- **Offline Password Cracking** — Dictionary-based attack demonstration
- **Brute-Force Simulation** — See how attackers actually work
- **Weakness Visualization** — Understand why weak passwords fail
- **Performance Metrics** — Measure attack speed vs. security

### ⚡ Cryptographic Performance Testing
- **SHA256 vs bcrypt** — Speed comparison reveals security trade-offs
- **Cost Factor Analysis** — Understand bcrypt's intentional slowness
- **Attack Feasibility** — Calculate time-to-crack for different algorithms

---

## 🏗️ Architecture

### System Flow

```
┌─────────────────────┐
│  User Input (CLI)   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Validation Layer    │
│ (username, pwd len) │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Authentication      │
│ (bcrypt hashing)    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Database Layer      │
│ (SQLite queries)    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Security State Mgr  │
│ (lockout tracking)  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Audit Logger        │
│ (audit.log file)    │
└─────────────────────┘
```

### Component Breakdown

| Component | Responsibility | Technology |
|-----------|-----------------|------------|
| **main.py** | CLI menu system, user navigation | Python click/input |
| **login.py** | Authentication logic, verification | bcrypt, database |
| **register.py** | User registration, validation | bcrypt, database |
| **database.py** | SQLite connection, schema, queries | sqlite3 |
| **logger.py** | Security event logging, audit trail | Python logging |
| **cracker.py** | Attack simulation, dictionary attacks | bcrypt, file I/O |
| **speed_test.py** | Performance benchmarking | hashlib, bcrypt, time |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/dhanuskiruthick/vault-cli.git
cd vault-cli

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies
```
bcrypt==4.0.1
```

That's it. Seriously.

---

## 📖 Usage Guide

### Main Menu
```
🔐 VAULT CLI - Authentication System
================================
1. Register new user
2. Login
3. Crack (Lab)
4. Speed Test
5. Exit
```

### Register a New User
```
$ python main.py
$ [Select option 1]
$ Enter username: alice
$ Enter password: ••••••••
$ Confirm password: ••••••••
✅ Registration successful! You can now login.
```

### Login
```
$ [Select option 2]
$ Enter username: alice
$ Enter password: ••••••••
✅ Login successful!
```

### View Audit Logs
```bash
# Check security events
cat audit.log

# Output:
# 2024-01-15 14:23:45 - LOGIN_SUCCESS - alice
# 2024-01-15 14:24:12 - LOGIN_FAILED - bob
# 2024-01-15 14:24:15 - LOGIN_FAILED - bob
# 2024-01-15 14:24:18 - LOGIN_FAILED - bob
# 2024-01-15 14:24:18 - ACCOUNT_LOCKED - bob
```

### Run Attack Simulation
```bash
# Test dictionary attack on user passwords
python cracker.py

# Output:
# Testing dictionary attack...
# Password 'password' cracked in 0.02 seconds
# Password '123456' cracked in 0.01 seconds
# Password 'MyStr0ng!Pwd' survived attack ✅
```

### Performance Comparison
```bash
# Compare SHA256 vs bcrypt speeds
python speed_test.py

# Output:
# SHA256: 150,000 hashes/second (FAST - INSECURE FOR PASSWORDS)
# bcrypt: 45 hashes/second (SLOW - SECURE BY DESIGN)
# Security Multiplier: 3,333x slower = 3,333x harder to crack
```

---

## 🧠 Key Security Learnings

### 1️⃣ Fast Hashing Is Dangerous

**The Problem**: SHA256 and MD5 are *too fast*.

```
SHA256: 100,000 hashes/second on modern hardware
Attack time for 6-char password: ~5 seconds
```

**Why It Matters**: Attackers can try millions of passwords cheaply.

### 2️⃣ bcrypt Makes Attacks Expensive

**The Solution**: bcrypt intentionally slows down hashing.

```
bcrypt (cost=12): 50 hashes/second
Attack time for 6-char password: ~2 days
```

**Cost Factor Trade-off**:
- Lower cost = faster, less secure
- Higher cost = slower, more secure
- Must balance user experience vs. security

### 3️⃣ Security Is About Trade-offs

**Lockout Mechanism**:
- ✅ Prevents brute-force attacks
- ❌ Vulnerable to account lockout DoS attacks
- ⚖️ Real systems use smarter detection

**There is no "perfect" security, only better solutions for your threat model.**

### 4️⃣ Logging Is a Security Responsibility

**Why Logs Matter**:
```
3 failed attempts in 30 seconds → Brute-force attempt
50 failures from different IPs → Distributed attack
```

**Critical Rule**: Never log sensitive data (passwords, tokens, secrets).

### 5️⃣ Understanding Attacks Improves Defense

By building an attacker's tool (the cracker), you understand:
- Why weak passwords are dangerous
- How dictionary attacks work
- What real attackers look for

---

## 📁 Project Structure

```
vault-cli/
│
├── main.py                  # CLI entry point & menu system
├── login.py                 # Authentication & verification logic
├── register.py              # Registration & validation
├── database.py              # SQLite connection & schema
├── logger.py                # Audit logging system
├── cracker.py               # Dictionary attack simulator (lab)
├── speed_test.py            # Hashing performance comparison
│
├── vault.db                 # SQLite database (auto-created)
├── audit.log                # Security event logs (auto-created)
├── requirements.txt         # Python dependencies
├── common_passwords.txt     # For dictionary attacks
│
└── README.md                # This file
```

---

## 💻 Example Workflows

### Scenario 1: Normal Login
```
User registers with password "MySecure!Pass123"
↓
Password hashed with bcrypt (cost=12)
↓
Stored in database (hash only, never plaintext)
↓
User logs in, enters password
↓
Entered password hashed and compared to stored hash
↓
✅ Match found → Login successful
↓
Log: LOGIN_SUCCESS, user=alice, timestamp=14:45:22
```

### Scenario 2: Brute-Force Attack Detection
```
Attacker tries: password, 123456, admin, ...
↓
Failed attempt 1 → Log: LOGIN_FAILED
Failed attempt 2 → Log: LOGIN_FAILED
Failed attempt 3 → Account locked for 15 minutes
↓
Log: ACCOUNT_LOCKED, user=victim, duration=900s
↓
Defender sees pattern in audit.log and blocks IP
```

### Scenario 3: Dictionary Attack (Lab)
```
Dictionary file: [password, 123456, qwerty, ...]
↓
For each word in dictionary:
  - Hash it with bcrypt
  - Compare to database hashes
  - If match found → Password cracked
↓
Results show which passwords are vulnerable
↓
Developer realizes users need stronger passwords
```

---

## ⚠️ Security Disclaimers

### What This Project Is NOT
- ❌ Production-ready authentication system
- ❌ Suitable for protecting real user data
- ❌ Replacement for industry frameworks
- ❌ Audited or reviewed by security professionals

### What This Project IS
- ✅ Educational demonstration of authentication concepts
- ✅ Learning tool for understanding security trade-offs
- ✅ Example of secure coding practices (for learning)
- ✅ Starting point for deeper security study

### If You Need Real Authentication
Use established libraries:
- **Python**: Django auth, FastAPI security, Flask-Login
- **General**: OAuth2, SAML, OpenID Connect
- **Enterprise**: Okta, Auth0, Cognito

---

## 🎯 Learning Outcomes

After working with this project, you'll understand:

1. ✅ Why plaintext passwords are terrible
2. ✅ How bcrypt actually improves security
3. ✅ Why slow hashing is a feature, not a bug
4. ✅ How to implement account lockout mechanisms
5. ✅ Why audit logging matters for security
6. ✅ How dictionary attacks work in practice
7. ✅ Security as a system of trade-offs
8. ✅ Difference between theory and implementation

---

## 🔮 Future Improvements (Planned)

- [ ] Multi-factor authentication (MFA)
- [ ] TOTP/SMS second factor
- [ ] Session token system
- [ ] JWT-based authentication
- [ ] Role-based access control (RBAC)
- [ ] Password strength meter
- [ ] REST API version
- [ ] Docker containerization
- [ ] Unit tests & integration tests
- [ ] Security audit logging improvements

---

## 📊 Performance Metrics

### Hashing Speed Comparison
| Algorithm | Speed | Use Case | Security Rating |
|-----------|-------|----------|-----------------|
| MD5 | 500K+ h/s | Checksums only | 🔴 UNSAFE |
| SHA256 | 100K+ h/s | Content, signatures | 🟡 WEAK for passwords |
| bcrypt (cost=10) | 1K h/s | Legacy | 🟢 GOOD |
| bcrypt (cost=12) | 50 h/s | Modern standard | 🟢 EXCELLENT |
| bcrypt (cost=14) | 5 h/s | High security | 🟢 EXCELLENT |

### Attack Feasibility (6-char password)
| Algorithm | Time to Crack | Feasible? |
|-----------|---------------|-----------|
| SHA256 | ~30 seconds | ✅ Yes |
| bcrypt (cost=10) | ~30 minutes | ✅ Yes (maybe) |
| bcrypt (cost=12) | ~2 days | ❌ No (practical) |
| bcrypt (cost=14) | ~2 weeks | ❌ No |

---

## 🐛 Known Limitations

1. **No rate limiting on login attempts** — Real systems use API-level rate limiting
2. **Simple lockout mechanism** — Vulnerable to DoS attacks on user accounts
3. **No password complexity validation** — Should enforce stronger requirements
4. **Audit logs are plaintext** — Should be encrypted, signed, and centralized
5. **No session management** — Real systems use tokens or encrypted sessions
6. **Single-threaded CLI** — Doesn't handle concurrent requests
7. **No HTTPS** — Obviously needed for any real system

---

## 📚 Resources for Further Learning

### Authentication & Hashing
- OWASP: Password Storage Cheat Sheet
- "Salted Password Hashing" by Enough Software
- bcrypt paper by Niels Provos & David Mazières

### Security Engineering
- "Security Engineering" by Ross Anderson
- "The Tangled Web" by Michal Zalewski
- OWASP Top 10

### Cryptography Basics
- "Cryptography 101" by Christof Paar
- Khan Academy: Cryptography
- "Understanding Cryptography" textbook

---

## 🤝 Contributing

This is a learning project. Contributions welcome!

Want to add:
- Better logging?
- More attack simulations?
- Performance optimizations?
- Additional security features?

Open an issue or submit a PR!

---

## ⚖️ License

[Choose appropriate license - MIT recommended for educational projects]

---

## 👤 About

Built by a first-year student who got tired of not understanding how authentication works, decided to build it, and accidentally learned more in 2 weeks than in a semester of classes.

If you're studying security, **build something**. Don't just read about it.

---

## 📮 Questions?

- Check the [Issues](./issues) page
- Read the inline code comments
- Review the Medium blog post for detailed explanations

---

**Remember**: The best way to understand security is to break it yourself. Go build something insecure, learn why it's insecure, then fix it.

That's how real security engineers are made.

---

**⭐ If this helped you understand authentication better, star the repo!**
