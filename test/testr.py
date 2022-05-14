from datetime import datetime
import cv2


def test(img):
    orb = cv2.AKAZE_create()
    kp = orb.detect(img, None)
    kp, des = orb.compute(img, kp)
    return des

now = datetime.now()

img = cv2.imread('./img.jpg')

imgs_lazy = [test(img) for _ in range(500)]

after = datetime.now()

print(after - now)