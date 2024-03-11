import cv2
import face_recognition
from utils.common_utils import get_default_logger


def capture_img(imgname, logger = get_default_logger()):
    logger.info("Press SpaceBar to take the photo")
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            raise 'failed to grab frame'
        cv2.imshow('test', img)
        k  = cv2.waitKey(1)
        if k%256 == 27:
            logger.info('escape hit, closing the program')
            raise "User Exists the program"
        elif k%256  == 32:
            logger.info('screenshot taken')
            face_locations = face_recognition.face_locations(img)

            if len(face_locations) == 1:
                cv2.imwrite(str(imgname), img)
                cap.release()
                cv2.destroyAllWindows()
                break
            else:
                logger.info(f"please take the photo again since detect {len(face_locations)}faces")






