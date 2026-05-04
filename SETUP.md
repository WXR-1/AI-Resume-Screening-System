# Quick Setup Guide

## Prerequisites

- Python 3.12 or later
- Ollama with a local LLM model installed
- 512MB available disk space

## Step 1: Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd ai-resume-screener

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Email (Optional)

```bash
python launcher.py --mode config
```

Follow the GUI prompts to configure your email provider. Skip if you want to run in dry-run mode.

## Step 3: Prepare Job Roles

Create a file with job descriptions (e.g., `roles.txt`):

```
Senior Software Engineer
5+ years Python experience, cloud deployment, team leadership

---

Data Scientist
ML expertise, statistical analysis, research background
```

## Step 4: Add Resumes

Place resume files in the `Resumes/` directory:
```
Resumes/
├── john_doe_resume.pdf
├── jane_smith_cv.pdf
└── ...
```

## Step 5: Run Screening

### GUI Mode (Recommended)
```bash
python launcher.py
```

Then:
1. Select your roles.txt file
2. Confirm Resumes directory is set
3. Check or uncheck "Dry Run Mode"
4. Click "Run Screening"

### CLI Mode
```bash
python launcher.py --mode cli --role-file roles.txt --dry-run
```

Remove `--dry-run` to actually send emails.

## Web Application

Start the HR portal:
```bash
cd recruitment_app
python app.py
```

Access at http://127.0.0.1:5000

- Applicants can submit resumes
- HR can login and manage candidates (default: hr / admin123 - change in .env for production)

## Troubleshooting

**"No module named 'ollama'"**
- Ensure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`

**Email test fails**
- Verify credentials in .env are correct
- For Gmail: use App Password, not regular password
- Test with: `python test_email.py your-email@example.com`

**Database errors**
- Delete and recreate: `rm recruitment_app/database.db`

## Next Steps

- Review README.md for full documentation
- Check MAIL_SETUP.md for email configuration details
- Customize HTML templates in recruitment_app/templates/
- Adjust LLM model in .env for different performance/quality tradeoff
