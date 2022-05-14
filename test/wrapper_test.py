from parallel_api.api.client_endpoint import ClientEndpoint
from parallel_api.api.wrapper import cluster_function
from datetime import datetime
import cv2
endpoint = ClientEndpoint(63345)


@cluster_function(endpoint=endpoint)
def test(img):
    orb = cv2.AKAZE_create()
    kp = orb.detect(img, None)
    kp, des = orb.compute(img, kp)
    return des

now = datetime.now()

img = cv2.imread('./img.jpg')

imgs_lazy = [test(img) for _ in range(100)]

imgs = [x.result for x in imgs_lazy]

after = datetime.now()

print(after - now)