app.config['CELERY_BROKER_URL'] = 'amqp://hngapp:mypassword123@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'
J