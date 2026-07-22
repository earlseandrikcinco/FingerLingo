
import cv2

webcam = cv2.VideoCapture(0) # the number is assigned to my laptop, might be different for you (try 1)


while True:
    ret, frame= webcam.read() 

    if ret == True:
        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1) & 0xFF #in millisecond
        if key == 27: #pressing the esc key will stop the camera essentially (doesn't close when you click the x button though)
            print("Closing the Webcam...")
            break
    else:
        break    

webcam.release()
cv2.destroyAllWindows()