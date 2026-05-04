# Email Configuration Guide

This guide explains how to configure SMTP email settings for sending selection notifications to candidates.

## Quick Start

### Option 1: Using the GUI Configuration Tool (Recommended)

```bash
python launcher.py --mode config
```

This launches an interactive setup window where you can:
1. Enter SMTP server details
2. Test the connection
3. Save your configuration

### Option 2: Manual Configuration

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your email credentials:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_ADDRESS=your-email@gmail.com
```

3. Test the connection:
```bash
python test_email.py recipient@example.com
```

## Provider-Specific Setup

### Gmail

**SMTP Settings:**
- Host: smtp.gmail.com
- Port: 587 (TLS)
- Username: your-email@gmail.com
- Password: App Password (NOT regular password)

**Setup Steps:**
1. Enable 2-Factor Authentication at https://myaccount.google.com/security
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character app password
5. Paste into SMTP_PASS field

### Outlook

**SMTP Settings:**
- Host: smtp-mail.outlook.com
- Port: 587 (TLS)
- Username: your-email@outlook.com
- Password: Your Outlook password

**Note:** New Outlook accounts require 24-48 hours before SMTP access is enabled.

### Office365

**SMTP Settings:**
- Host: smtp.office365.com
- Port: 587 (TLS)
- Username: your-email@company.com
- Password: Your Office365 password

### Yahoo Mail

**SMTP Settings:**
- Host: smtp.mail.yahoo.com
- Port: 587 (TLS)
- Username: your-email@yahoo.com
- Password: App Password

**Setup Steps:**
1. Go to https://login.yahoo.com
2. Click "Generate app password"
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character password
5. Paste into SMTP_PASS field

### Custom Email Server

Contact your email provider or IT department for:
- SMTP server address
- SMTP port (typically 587 for TLS or 465 for SSL)
- Email username/address
- Password or app-specific password

## Testing

### Using GUI

1. Run: `python launcher.py --mode config`
2. Enter your SMTP details
3. Click "Test Email Connection"
4. If successful, click "Save Configuration"

### Using Command Line

```bash
python test_email.py your-test-email@example.com
```

Or with interactive prompt:
```bash
python test_email.py
# Enter recipient email when prompted
```

## Running with Email

### GUI Mode

1. Run: `python launcher.py`
2. Uncheck "Dry Run Mode" to send actual emails
3. Click "Run Screening"

### CLI Mode

```bash
# Dry run (simulate without sending)
python launcher.py --mode cli --role-file roles.txt --dry-run

# Actually send emails
python launcher.py --mode cli --role-file roles.txt
```

## Troubleshooting

### "Username or password is incorrect"

- Verify credentials are correct
- For Gmail: ensure you're using an App Password, not your regular password
- For new Outlook accounts: wait 24-48 hours before trying again
- Check if 2FA is enabled and required by your provider

### "SMTP connection refused"

- Verify SMTP_HOST and SMTP_PORT are correct
- Try port 465 (SSL) instead of 587 (TLS)
- Check if your firewall/antivirus is blocking SMTP

### ".env file not found"

```bash
cp .env.example .env
python launcher.py --mode config
```

### Email sent but not received

- Check spam/junk folder
- Verify recipient email address is correct
- Check email logs: `python test_email.py recipient@example.com`

## Security Best Practices

1. Never commit .env file to version control (already in .gitignore)
2. Use app-specific passwords for Gmail, Yahoo, and other providers
3. Change credentials periodically
4. Don't share .env file with unauthorized users
5. Use environment-specific configurations for production

## Disabling Email

To run without email configuration:
1. Leave SMTP fields empty in .env
2. Always use dry-run mode: `--dry-run` flag
3. Check "Dry Run Mode" in GUI

## Production Deployment

For production environments:
- Use environment variables instead of .env file
- Set up email account dedicated to application use
- Configure application-specific IP allowlists if supported
- Monitor email delivery logs
- Set up backup SMTP server for reliability
