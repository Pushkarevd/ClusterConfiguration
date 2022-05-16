from datetime import datetime
import cv2


def batch_factorial(batch):
    result = 1
    for i in batch:
        result *= i
    return result

now = datetime.now()

batch_factorial(range(1, 1_000_000))

after = datetime.now()

print(f'Basic factorial - {after - now}')