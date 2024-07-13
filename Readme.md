# Messaging System with RabbitMQ/Celery and Python Application behind Nginx
## Table of Contents
### 1. Introduction
### 2. Project Overview
### 3. Prerequisites
### 4. Step-by-Step Guide
1. Setting up the Virtual Machine
2. Installing Required Software
3. Setting up RabbitMQ
4. Creating the Python Environment
5. Developing the Python Application
6. Configuring Nginx
7. Running the Application
8. Testing the Application
9. Exposing the Application with ngrok

### 5. Troubleshooting Common Issues
### 6. Conclusion

### Introduction
This README provides a comprehensive guide to setting up a messaging system using RabbitMQ, Celery, and a Python application served behind Nginx. This project demonstrates how to create a robust, scalable system for handling asynchronous tasks like sending emails and logging messages.

### Project Overview
The project consists of a Python application that exposes two main functionalities:
1. Sending emails asynchronously using Celery and RabbitMQ
2. Logging messages to a file

These functionalities are accessed through HTTP endpoints, which are served by a Flask application running behind Nginx.

### Prerequisites

1. A Virtual Machine (VM) or a server (We'll use DigitalOcean in this guide)
2. Basic knowledge of Linux command line
3. A domain name (optional, but recommended for production use)

### Step-by-Step Guide
#### Setting up the Virtual Machine
1. Create a new Droplet on DigitalOcean
    - Choose Ubuntu 20.04 LTS x64
    - Select a plan that fits your needs (2GB/1CPU is sufficient for this project)
    - Choose a datacenter region close to your target audience
    - Add your SSH key for secure access

2. Once the Droplet is created, connect to it via SSH  
```
ssh root@your_droplet_ip
```

#### Installing Required Software
Update the system and install necessary packages:
```
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip nginx rabbitmq-server -y
```
This installs Python, pip (Python package manager), Nginx (web server), and RabbitMQ (message broker).

```
python3 --version
pip3 --version
nginx -v
rabbitmq-server --version
```
This verifies that they are running. 

#### Setting up RabbitMQ
1. Start and enable RabbitMQ:
```
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

#### I encountered permission issues here and this is how i resolved it 
```
ls -l /var/lib/rabbitmq
```
- Make sure the directories and files are owned by the rabbitmq user.
- Verify that the RabbitMQ user has the correct permissions:
```
sudo chown -R rabbitmq:rabbitmq /var/lib/rabbitmq
```
I ran RabbitMQ in the foreground to see any error messages directly and they were still erros
```
sudo rabbitmq-server
```
This will start RabbitMQ in the foreground and show you any startup errors directly in the console.

I had to check the Erlang cookie:
```
sudo ls -l /var/lib/rabbitmq/.erlang.cookie
sudo ls -l /root/.erlang.cookie
```
Both files should exist and have the same content. If they don't:
```
sudo cp /var/lib/rabbitmq/.erlang.cookie /root/.erlang.cookie
sudo chmod 400 /root/.erlang.cookie
sudo chown root:root /root/.erlang.cookie
```
After making these changes, try to start RabbitMQ again:

2. Check RabbitMQ status:
```
sudo systemctl status rabbitmq-server
```
3. Create a RabbitMQ user for our application:
```
sudo rabbitmqctl add_user hngapp mypassword123
sudo rabbitmqctl set_user_tags hngapp administrator
sudo rabbitmqctl set_permissions -p / hngapp ".*" ".*" ".*"
```
These commands create a user named "hngapp" with the password "mypassword123" and grant it administrator privileges.

#### Creating the Python Environment
1. Create a directory for our project:
```
mkdir messaging_system && cd messaging_system
```
2. Create a virtual environment:
```
python3 -m venv venv
```
3. Activate the virtual environment:
```
source venv/bin/activate
```
4. Install required Python packages:
```
pip install flask celery[rabbitmq] gunicorn
```

#### Developing the Python Application
1. Create `celery_app.py`
```
from celery import Celery
import smtplib
from email.mime.text import MIMEText
import logging

app = Celery('tasks', 
             broker='amqp://hngapp:mypassword123@localhost//',
             backend='rpc://')

@app.task
def send_email(recipient):
    logging.basicConfig(filename='/var/log/celery_tasks.log', level=logging.INFO)
    
    try:
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "your_email@gmail.com"
        password = "your_app_password"

        message = MIMEText("This is a test email from your messaging system.")
        message['Subject'] = "Test Email"
        message['From'] = sender_email
        message['To'] = recipient

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient, message.as_string())
        
        logging.info(f"Email sent successfully to {recipient}")
        return f"Email sent to {recipient}"
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}. Error: {str(e)}")
        raise
```

2. Create `flask_app.py`:
```
from flask import Flask, request
from celery_app import app as celery_app, send_email
import logging
from datetime import datetime

app = Flask(__name__)

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
        return "Invalid request. Use ?sendmail=email@example.com or ?talktome"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

#### To start running test on the application
```
celery -A celery_app worker --loglevel=info
python main_app.py
python celery_app.py
```
#### Configuring Nginx
1. Create a new Nginx configuration file:
```
sudo nano /etc/nginx/sites-available/messaging_system
```
2. Add the following configuration:
```
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain or server IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
3. Enable the site:
```
sudo ln -s /etc/nginx/sites-available/messaging_system /etc/nginx/sites-enabled/
```
4. Test Nginx configuration:
```
sudo nginx -t
```
5. If the test is successful, restart Nginx:
```
sudo systemctl restart nginx
```
#### Running the Application

1. Start the Celery worker:
```
celery -A celery_app worker --loglevel=info
```
2. In a new terminal window, start the Flask application using Gunicorn:
```
sudo apt install gunicorn
# install Flask and other required packages
pip install flask celery[rabbitmq] gunicorn

# Verify that Flask is installed
pip list | grep Flask

# To run the application
gunicorn --bind 0.0.0.0:8000 flask_app:app
# I encountered some issues, so i used
~/messaging_system/venv/bin/gunicorn --bind 0.0.0.0:8000 flask_app:app

python flask_app.py
```


### Testing the Application

1. To test the email sending functionality:
```
curl "http://your_server_ip/?sendmail=test@example.com"
```

2. To test the logging functionality:
```
curl "http://your_server_ip/?talktome"
```
3. Check the logs:
```
sudo tail -f /var/log/messaging_system.log
sudo tail -f /var/log/celery_tasks.log
```

#### Exposing the Application with ngrok
1. Install ngrok:
```
snap install ngrok
```
2. Expose your application:
```
ngrok http 80
```
Use the provided ngrok URL to access your application from the internet.

### Troubleshooting Common Issues

1. RabbitMQ Connection Issues:
    - Ensure RabbitMQ is running: `sudo systemctl status rabbitmq-server`
    - Verify user credentials: `sudo rabbitmqctl list_users`

2. Email Sending Failures:
    - Double-check SMTP settings in `celery_app.py`
    - Ensure you're using an **app password for Gmail**
    - Check `/var/log/celery_tasks.log` for detailed error messages

3. Nginx Configuration Issues:
    - Verify Nginx is running: `sudo systemctl status nginx`
    - Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

4. Permission Issues:
    - Ensure log files are writable:
```
sudo touch /var/log/messaging_system.log /var/log/celery_tasks.log
sudo chown www-data:www-data /var/log/messaging_system.log /var/log/celery_tasks.log
```

### Conclusion
This project demonstrates how to set up a messaging system using RabbitMQ, Celery, and a Python application served behind Nginx. It provides a scalable architecture for handling asynchronous tasks like sending emails and logging messages.
By following this guide, you've learned how to:

- Set up a Virtual Machine
- Install and configure RabbitMQ
- Develop a Python application with Flask and Celery
- Configure Nginx as a reverse proxy
- Use ngrok to expose your local server to the internet

This setup can be extended to handle more complex tasks and can serve as a foundation for larger, more sophisticated messaging systems.