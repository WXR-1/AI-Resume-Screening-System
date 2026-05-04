# AI Resume Screening System

An intelligent resume screening system with dual interfaces: AI-powered agent-based analysis and a modern web application for applicant submissions and HR management.

## Features

### AI Screening Engine
- Automatic resume parsing and validation
- LLM-powered candidate ranking against job requirements
- Multi-role candidate assignment and matching
- Configurable email notifications for selected candidates
- Local processing with Ollama (no cloud dependency)

### Web Application
- Public applicant submission portal with resume upload
- HR login and secure dashboard
- Candidate management (Select, Reject, Delete)
- Resume viewing and tracking
- Session-based authentication with 8-hour timeout
- URL-based access control

### Desktop GUI
- Graphical interface for AI screening operations
- Email configuration tool
- Test email functionality
- Real-time execution logs

## Project Structure

```
.
├── agents/                      # AI agent modules
│   ├── orchestrator.py          # Main orchestration agent
│   ├── resume_reader.py         # Resume parsing
│   ├── role_matcher.py          # Role-candidate matching
│   ├── candidate_ranker.py      # Candidate ranking
│   ├── validation_agent.py      # Resume validation
│   ├── mail_sender.py           # Email sending
│   └── llm_client.py            # Ollama LLM integration
├── recruitment_app/             # Flask web application
│   ├── app.py                   # Web server and routes
│   ├── templates/               # HTML templates
│   └── static/                  # CSS and assets
├── config.py                    # Configuration constants
├── main.py                      # CLI entrypoint
├── launcher.py                  # Multi-mode launcher (GUI/CLI/Config)
├── gui.py                       # Desktop GUI application
├── mail_config.py               # Email configuration tool
├── test_email.py                # Email testing utility
├── Resumes/                     # Resume storage directory
└── requirements.txt             # Python dependencies
```

## Requirements

- Python 3.12+
- Ollama with a local LLM model (Mistral, Llama2, or Neural-Chat)
- Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-resume-screener
```

2. Create a Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment configuration:
```bash
cp .env.example .env
```

5. Configure email (optional):
```bash
python launcher.py --mode config
```

## Usage

### Desktop GUI (Recommended)

Start the multi-mode launcher:
```bash
python launcher.py
```

This opens a graphical interface for:
- Selecting job role files
- Choosing resume directories
- Running candidate screening
- Viewing real-time logs

### Command Line Interface

Run screening with specific parameters:
```bash
python launcher.py --mode cli --role-file jobs.txt --model mistral
```

Options:
- `--role-file`: Path to role description file (required for CLI)
- `--model`: Override default Ollama model
- `--dry-run`: Simulate without sending emails

### Email Configuration

Configure SMTP settings for email notifications:
```bash
python launcher.py --mode config
```

Supported providers: Gmail, Outlook, Office365, Yahoo, custom servers.

### Web Application

Start the recruitment web portal:
```bash
cd recruitment_app
python app.py
```

Access at: http://127.0.0.1:5000

Features:
- Public application form for candidates
- HR dashboard with secure login (default credentials: hr / admin123 - change in .env for production)
- Candidate management tools

### Test Email

Verify email configuration:
```bash
python test_email.py recipient@example.com
```

## Configuration

### Environment Variables (.env)

```
# Ollama LLM
OLLAMA_MODEL=mistral

# SMTP Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_ADDRESS=your-email@gmail.com

# Optional: Database settings (if using remote DB)
DB_HOST=localhost
DB_NAME=resume_screener
DB_USER=user
DB_PASS=password
```

### Role File Format

Create a text file with job descriptions:
```
Senior Software Engineer with 5+ years Python experience, cloud deployment knowledge, and team leadership.

---

Data Scientist with machine learning expertise, statistical analysis skills, and research publication experience.
```

Separate multiple roles with `---` or blank lines.

## Security Notes

- The `.env` file contains sensitive credentials and is excluded from version control
- Default HR credentials (hr / admin123) MUST be changed in production via .env file
- Flask SECRET_KEY should be regenerated for production
- Use app-specific passwords for email accounts (Gmail, Yahoo)
- Session cookies are secure (HTTPONLY, SAMESITE, 8-hour timeout)
- All database access is parameterized to prevent injection
- HTTPS should be enforced in production
- Consider using a production WSGI server (not Flask development server)

## Troubleshooting

### Ollama Connection Issues
Ensure Ollama is running:
```bash
ollama serve
```

Verify model availability:
```bash
ollama list
```

### Email Configuration
- Gmail: Use 2FA + App Password, not regular password
- Outlook: New accounts may require 24-48 hours for SMTP activation
- Port 587 (TLS) or 465 (SSL) depending on provider

### Database Issues
Database is automatically created on first run. To reset:
```bash
rm recruitment_app/database.db
```

## Development

### Adding New Email Providers
Edit `mail_config.py` to add provider configurations in the "Common Email Providers" section.

### Customizing Resume Parsing
Modify `agents/resume_reader.py` to add support for additional file formats.

### Extending the Web UI
Templates are in `recruitment_app/templates/` and styling in `recruitment_app/static/style.css`.

## License

This project is provided as-is for educational and internal use.

## Support

For issues or questions, refer to the documentation files:
- `MAIL_SETUP.md` - Email configuration guide
- Code comments in `agents/` directory
