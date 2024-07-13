from celery_app import add

result = add.delay(4, 4)
print(f"Task ID: {result.id}")
print(f"Result: {result.get(timeout=10)}")  # This should print 8
