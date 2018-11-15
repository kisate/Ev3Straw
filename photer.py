import cv2

cap = cv2.VideoCapture(2)

counter = 0

while True:
    _, frame = cap.read()
    cv2.imshow('photer', frame)

    k = cv2.waitKey(1)

    if k == ord('a') :
        cv2.imwrite('../eval/img{}.png'.format(counter), frame)
        counter+=1
    if k == ord('q') :
        cap.release()
        cv2.destroyAllWindows()

cap.release()