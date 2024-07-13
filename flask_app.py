from flask import Flask, request
from celery_app import app as celery_app, send_email
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='/var/log/messaging_system.log', level=logging.INFO)

@app.route('/')
def handle_request():
    if 'sendmail' in request.args:
        recipient = request.args.get('sendmail')
        task = send_email.delay(recipient)
        return f"Email sending task queued for {recipient}. Task ID: {task.id}"
    elif 'talktome' in request.args:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Talktome request received at {current_time}")
        return f"Current time logged: {current_time}"
    else:
        return "Invalid request. Use ?sendmail=abiegbeg@gmail.com or ?talktome"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
