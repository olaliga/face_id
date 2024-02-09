import face_recognition
import cv2, os
import numpy as np
from utils.db_utils import UserDB
from utils.common_utils import log, timing, get_default_logger

class Camara:
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        
    def preprocess(self, frame):
        small_frame = cv2.resize(frame, (0,0), fx=0.25, fy = 0.25)
        return small_frame


class FaceId:
    def __init__(self, user_db_path, logger = get_default_logger()):
        self.user_database = UserDB(user_db_path)
        self.camara = Camara()
        self.logger = logger
    @timing
    def detect(self):
        username = None
        try :
            while username is None :
                ret, tmp_frame = self.camara.video_capture.read()
                frame = self.camara.preprocess(tmp_frame)
                self.logger.info("Get Frame and recognize face")
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                self.logger.info("start match faces")
                username = self.match_db_faces(face_encodings) 
                self.logger.info(f"user is {username}")
        except:
            self.release()
            raise Exception("detection error")
        return username
    @timing
    def match_db_faces(self, face_encodings):
        match_dict = {}
        for face_encoding in face_encodings:
            self.logger.info("Get Face Encodings")
            known_face_encodings_dict = self.user_database.get_face_ecoding_dict()
            # See if the face is a match for the known face(s)
            self.logger.info(f"number of users : {len(known_face_encodings_dict)}")
            if len(known_face_encodings_dict) == 0:
                raise Exception("Fail to access DB")
            self.logger.info("Comparing Faces")
            for username, known_face_encodings in known_face_encodings_dict.items():
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, 0.5)
                match_dict.update({username : np.mean(matches)})
            
            username = max(match_dict, key = match_dict.get)
            if match_dict[username] > 0.9:
                return username
            else:
                return None

    def is_login(self, username):
        if username is not None :
            return True
        return False
    @timing
    def get_password(self, username):
        password = self.user_database[username].get_password()
        return password
            
    def release(self):
        # Release handle to the webcam
        self.camara.video_capture.release()
        cv2.destroyAllWindows()

    #def debug(self):


