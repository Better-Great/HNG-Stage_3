from celery import Celery
import smtplib
from email.mime.text import MIMEText
import logging

app = Celery('tasks',
             broker='amqp://hngapp:mypassword123@localhost//',
             backend='rpc://')

@app.task
def add(x, y):
    return x + y

@app.task
def subtract(x, y):
    return x - y

@app.task
def multiply(x, y):
    return x * y

@app.task
def divide(x, y):
    if y == 0:
        return 'Cannot divide by zero!'
    return x / y

@app.task
def send_email(recipient):
    # Configure logging
    logging.basicConfig(filename='/var/log/celery_tasks.log', level=logging.INFO)

    try:
        # SMTP settings
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "abiegbeg@gmail.com"
        password = "your-app-password"
        recipient_email = "destiny@destinedcodes.com"

        message = MIMEText("This is a test email from your messaging system.")
        message['Subject'] = "Test Email"
        message['From'] = sender_email
        message['To'] = recipient_email

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        logging.info(f"Email sent successfully to {recipient_email}")
        return f"Email sent to {recipient_email}"
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}. Error: {str(e)}")
        raise  # Re-raise the exception so Celery knows the task failed

if __name__ == '__main__':
    print(app.tasks)
                                                                                     
