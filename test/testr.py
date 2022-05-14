from datetime import datetime

def foo(x, y):
    return x ** 2 + y ** 2

now = datetime.now()
lazy_tasks = [foo(x, x ** .5) for x in range(10000)]

after = datetime.now()
print(after - now)