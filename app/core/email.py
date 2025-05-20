import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

from fastapi import BackgroundTasks
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings
from app.logger import logger

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        self.templates_dir = Path(__file__).parent.parent / "email-templates"
        
        # Ensure templates directory exists
        self.templates_dir.mkdir(exist_ok=True)
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_email(
        self,
        email_to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Send an email using the specified template and context.
        
        Args:
            email_to: Recipient email address
            subject: Email subject
            template_name: Name of the template file (without extension)
            context: Dictionary with template variables
            background_tasks: Optional FastAPI BackgroundTasks instance for async sending
        """
        # Add common context variables
        context.setdefault("project_name", settings.PROJECT_NAME)
        context.setdefault("frontend_url", settings.FRONTEND_URL)
        
        # Render email content
        html_content = self._render_template(f"{template_name}.html", context)
        text_content = self._render_template(f"{template_name}.txt", context)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = email_to
        
        # Attach both HTML and plain text versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email (sync or async)
        if background_tasks:
            background_tasks.add_task(self._send_sync, msg)
        else:
            await self._send_async(msg)
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    async def _send_async(self, msg: MIMEMultipart) -> None:
        """Send email asynchronously."""
        try:
            await self._send_sync(msg)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    def _send_sync(self, msg: MIMEMultipart) -> None:
        """Send email synchronously."""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if settings.SMTP_TLS:
                    server.starttls(context=context)
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
                logger.info(f"Email sent to {msg['To']}")
                
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

# Singleton instance
email_service = EmailService()

# Helper functions for common email types

async def send_new_account_email(
    email_to: str, 
    username: str,
    password: Optional[str] = None,
    background_tasks: Optional[BackgroundTasks] = None
) -> None:
    """Send account creation email with login details."""
    subject = f"Welcome to {settings.PROJECT_NAME}!"
    context = {
        "project_name": settings.PROJECT_NAME,
        "username": username,
        "password": password,
        "login_url": f"{settings.FRONTEND_URL}/login"
    }
    
    await email_service.send_email(
        email_to=email_to,
        subject=subject,
        template_name="welcome_email",
        context=context,
        background_tasks=background_tasks
    )

async def send_reset_password_email(
    email_to: str,
    token: str,
    username: str,
    background_tasks: Optional[BackgroundTasks] = None
) -> None:
    """Send password reset email with reset link."""
    subject = f"{settings.PROJECT_NAME} - Password Reset"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    context = {
        "project_name": settings.PROJECT_NAME,
        "username": username,
        "reset_url": reset_url,
        "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
    }
    
    await email_service.send_email(
        email_to=email_to,
        subject=subject,
        template_name="reset_password_email",
        context=context,
        background_tasks=background_tasks
    )

async def send_test_email(
    email_to: str,
    background_tasks: Optional[BackgroundTasks] = None
) -> None:
    """Send a test email."""
    subject = f"{settings.PROJECT_NAME} - Test Email"
    context = {
        "project_name": settings.PROJECT_NAME,
        "message": "This is a test email to verify email functionality."
    }
    
    await email_service.send_email(
        email_to=email_to,
        subject=subject,
        template_name="test_email",
        context=context,
        background_tasks=background_tasks
    )
