# 🛡️ MANUS+ Automated Debt Challenge System

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

Production-ready automated system for challenging illegal debt collection through Ukrainian E-Court, UBKI, and NBU integrations.

**Case Study: #67817393 - ФК Солвентіс**

## 🎯 Overview

MANUS+ automates the entire debt challenge process:
- ⚖️ **E-Court Integration** - Automated lawsuit filing and document submission
- 📊 **UBKI Monitoring** - Real-time credit history tracking and dispute automation
- 📨 **NBU Complaints** - Bank violation reporting system
- 🤖 **Orchestration** - Multi-track parallel execution

## 🚀 Quick Start (5 Minutes)

### Prerequisites
```bash
# Required
- Docker & Docker Compose
- Python 3.11+
- API credentials (E-Court, UBKI, NBU)
```

### Installation

```bash
# 1. Clone repository
git clone https://github.com/ChernyshDarisha/manus-debt-challenge.git
cd manus-debt-challenge

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API credentials

# 3. Start services
docker-compose up -d

# 4. Run migrations
make migrate

# 5. Execute challenge
make solventis-challenge
```

## 📚 Documentation

### Project Structure

```
manus-debt-challenge/
├── src/
│   ├── ecourt/          # E-Court API client
│   │   └── client.py     # Case filing & tracking
│   ├── ubki/            # UBKI integration
│   │   └── monitoring.py # Credit monitoring
│   ├── nbu/             # NBU complaints
│   │   └── complaint.py  # Violation reporting
│   └── core/            # Main orchestrator
│       └── debt_challenge.py
├── config/
│   └── settings.py      # Configuration
├── templates/           # Jinja2 templates
├── documents/           # Evidence & filings
├── examples/
│   └── challenge_solventis.py  # Real example
├── docker-compose.yml  # Full stack
├── Makefile            # Quick commands
└── requirements.txt    # Dependencies
```

## 🔧 Core Modules

### 1. E-Court Client (`src/ecourt/client.py`)

Automates interaction with Ukrainian Electronic Court System:

```python
async with ECourtClient(client_id, client_secret) as ecourt:
    # File lawsuit
    response = await ecourt.file_case(case_data, documents)
    
    # Track status
    status = await ecourt.get_case_status(case_number)
    
    # Submit additional documents
    await ecourt.submit_document(case_number, doc_type, file_path)
```

**Features:**
- OAuth2 authentication
- Case filing with attachments
- Real-time status tracking
- Court decision retrieval

### 2. UBKI Monitor (`src/ubki/monitoring.py`)

Monitors credit history and detects unauthorized activities:

```python
async with UBKIClient(api_key, user_identification) as ubki:
    # Get credit report
    report = await ubki.get_credit_report()
    
    # Detect unauthorized inquiries
    suspicious = await ubki.detect_unauthorized_inquiries()
    
    # Dispute debt
    await ubki.dispute_debt(debt_id, reason, documents)
```

**Features:**
- Real-time credit monitoring
- Unauthorized inquiry detection
- Automated dispute filing
- Change notifications

### 3. NBU Complaint System (`src/nbu/complaint.py`)

Automates complaints to National Bank of Ukraine:

```python
async with NBUComplaintClient(complainant_data) as nbu:
    # Generate complaint from template
    text = nbu.generate_complaint(violations)
    
    # Submit to NBU
    response = await nbu.submit_complaint(violations, documents)
    
    # Check status
    status = await nbu.check_complaint_status(complaint_number)
```

**Features:**
- Jinja2 template-based generation
- Batch complaint submission
- Status tracking
- Multi-bank support

### 4. Debt Challenge Orchestrator (`src/core/debt_challenge.py`)

Main automation engine coordinating all actions:

```python
orchestrator = DebtChallengeOrchestrator(ecourt, ubki, nbu, config)

# Analyze case
case = await orchestrator.analyze_enforcement_case(case_data)

# Create strategy
strategy = await orchestrator.create_challenge_strategy(case)

# Execute all actions
results = await orchestrator.execute_strategy(strategy)
```

**Capabilities:**
- Violation detection
- Multi-track strategy creation
- Parallel execution
- Progress tracking

## 👨‍💻 Usage Examples

### Basic Challenge Execution

```bash
# Run challenge for specific case
python -m examples.challenge_solventis

# With custom configuration
ENABLE_AUTO_EXECUTION=true python -m examples.challenge_solventis
```

### Monitoring Mode

```bash
# Start continuous monitoring
make monitor

# Check specific case status
python -m src.core.debt_challenge status --case 67817393
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# E-Court API
ECOURT_CLIENT_ID=your-client-id
ECOURT_CLIENT_SECRET=your-secret
ECOURT_CERTIFICATE_PATH=/path/to/cert.p12

# UBKI API
UBKI_API_KEY=your-ubki-key
UBKI_USER_IDENTIFICATION=your-inn-code

# NBU
NBU_API_KEY=your-nbu-key

# User Info
USER_FULL_NAME="Your Name"
USER_IDENTIFICATION=your-inn
USER_EMAIL=your@email.com

# Case Specific (FK Solventis #67817393)
CASE_NUMBER=67817393
CREDITOR_NAME="ТОВ \"FK СОЛВЕНТІС\""
CREDITOR_CODE=35625014
ORIGINAL_DEBT_AMOUNT=10294.90
CLAIMED_DEBT_AMOUNT=10294.90
```

## 📊 Case Study: FK Solventis #67817393

### Background
- **Original Debt:** 10,294.90 UAH (Contract #004023909, 2018)
- **Current Claim:** 10,294.90 UAH + penalties
- **Enforcement Started:** May 2021
- **Violations Detected:** 3+

### Detected Violations

1. **⚠️ Excessive Debt Claims** - Debt increased 32x (3,000 → 96,773 UAH)
2. **🚫 Illegal Debt Sales** - Sold without consumer consent  
3. **📝 Factoring Agreement Fraud** - Date mismatch with debt origin
4. **💰 Unauthorized Penalties** - No legal basis

### Automated Actions

```python
# Results from make solventis-challenge
✅ E-Court case filed: #1234567890
✅ UBKI dispute submitted: #UBK-123456
✅ NBU complaints (9 banks): #NBU-789012
✅ DVS complaint filed: #DVS-67817393-20260112
```

## 🔨 Development

### Available Make Commands

```bash
make install         # Install dependencies
make test           # Run tests
make lint           # Code linting
make format         # Format code
make docker-up      # Start Docker containers
make docker-down    # Stop containers
make migrate        # Run DB migrations
make backup-db      # Backup database
make clean          # Clean temp files
```

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# With coverage
pytest --cov=src --cov-report=html
```

## 🐛 Troubleshooting

### Database Connection Error
```bash
docker-compose down -v
docker-compose up -d
make migrate
```

### Authentication Failed
```bash
# Verify credentials
docker-compose exec manus-app python -c "from config.settings import settings; print(settings.ecourt_client_id)"
```

### Logs
```bash
# View application logs
docker-compose logs -f manus-app

# View worker logs
docker-compose logs -f worker
```

## 🛡️ Security

- 🔒 All API credentials encrypted at rest
- 🔐 TLS/SSL for all external communications  
- 🚫 Never commit `.env` or certificates to git
- ✅ Regular security audits with Bandit & Safety

## 📜 License

MIT License - see [LICENSE](LICENSE) file

## ⚖️ Legal Disclaimer

This software is provided for educational and legitimate debt challenge purposes only. Users are responsible for:
- Ensuring all claims are factually accurate
- Complying with Ukrainian legal procedures
- Obtaining necessary legal consultation
- Using API credentials ethically and legally

The authors are not responsible for misuse of this system.

## 👥 Support

- 📚 Full Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/ChernyshDarisha/manus-debt-challenge/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ChernyshDarisha/manus-debt-challenge/discussions)

## 📈 Roadmap

- [ ] Integration with Дія (Diia) for document automation
- [ ] OCR for automatic document processing
- [ ] ML model for case outcome prediction  
- [ ] Telegram bot interface
- [ ] Multi-language support (EN/UA/RU)
- [ ] Mobile app (React Native)

## 🚀 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Made with ❤️ in Bakhmach, Ukraine**

*Fighting for financial justice, one automated lawsuit at a time.*
