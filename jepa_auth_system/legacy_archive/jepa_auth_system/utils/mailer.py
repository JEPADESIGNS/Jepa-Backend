"""
utils/mailer.py — Background email notifications for security alerts.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

# Core Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_system_email@gmail.com"  # Replace with your SMTP email address
SENDER_PASSWORD = "your_app_password"          # Replace with your generated App Password

def _send_email_async(to_email: str, subject: str, body: str):
    """Internal runner to safely execute SMTP transfers without blocking Tkinter."""
    try:
        msg = MIMEMultipart()
        msg["From"] = f"JEPA Security <{SENDER_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"[SMTP Error] Failed to send email alert to {to_email}: {e}")

def send_security_alert(to_email: str, event_type: str, details: str):
    """Spawns a separate daemon thread to fire email notifications instantly."""
    if not to_email:
        return
        
    subject = f"Security Notification: {event_type.upper()}"
    body = (
        f"Hello,\n\n"
        f"This is an automated alert regarding your JEPA account.\n\n"
        f"Security Event: {event_type}\n"
        f"Details: {details}\n\n"
        f"If you did not authorize this change, please contact your administrator immediately."
    )
    # daemon=True ensures that if the user closes the main app, the thread won't hang it open
    threading.Thread(target=_send_email_async, args=(to_email, subject, body), daemon=True).start()