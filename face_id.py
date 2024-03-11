import face_recognition
import cv2, os
import numpy as np
from utils.db_utils import UserDB
from utils.common_utils import log, timing, get_default_logger

class Camara:
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        self.resize_scale = 0.25
        self.current_frame = 0

    def get_frame(self):
        __, tmp_frame = self.video_capture.read()
        self.current_frame = tmp_frame
        frame = self.preprocess(tmp_frame)
        return frame

    def preprocess(self, frame):
        small_frame = cv2.resize(frame, (0,0), fx=self.resize_scale, fy = self.resize_scale)
        return small_frame

    def show_frame(self, face_locations, faces_in_the_frame, frame):
        frame = self.current_frame
        for (top, right, bottom, left), info in zip(face_locations, faces_in_the_frame):
            name = info["username"] 
            prob = info["probs"]
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= (1/self.resize_scale)
            right *= (1/self.resize_scale)
            bottom *= (1/self.resize_scale)
            left *= (1/self.resize_scale)

            top = int(top)
            right = int(right)
            bottom = int(bottom)
            left = int(left)
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name +" prob : "+ str(round(prob, 3)), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # Display the resulting image
        cv2.imshow('Video', frame)

        
class FaceId:
    def __init__(self, configs, logger = get_default_logger()):
        self.configs = configs
        self.user_db_path = configs.get_user_db_path()
        self.debug_mode = True if configs.is_debug() else False
        self.user_database = UserDB(self.user_db_path)
        self.camara = Camara()
        self.logger = logger
        self.faces_in_the_frame = []

    @timing
    def detect(self):
        username = None
        try :
            while username is None :
                frame = self.camara.get_frame() 
                self.logger.info("Get Frame and recognize face")
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                self.logger.info("start match faces")
                
                username = self.match_db_faces(face_encodings) 
                if self.debug_mode:
                    self.show_real_time_detection(face_locations, frame)
                    # Hit 'q' on the keyboard to quit!
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                self.logger.info(f"user is {username}")
        except:
            self.release()
            raise Exception("detection error")
        return username
    
    def show_real_time_detection(self, face_locations, frame):
        self.camara.show_frame(face_locations, self.faces_in_the_frame, frame)
        
    @timing
    def match_db_faces(self, face_encodings):
        tmp_matching_dict = {}
        tmp_face_in_the_frame = []
        unknown_username = "Unknown"

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
                tmp_matching_dict.update({username : np.mean(matches)})
            
            username = max(tmp_matching_dict, key = tmp_matching_dict.get)
            tmp_probs = tmp_matching_dict[username]

            # only not in debug and match any faces in the database will return the username
            if tmp_probs > 0.9:
                tmp_face_in_the_frame.append({"username": username, 
                                                "probs" : tmp_probs})
            else:
                tmp_face_in_the_frame.append({"username": unknown_username,
                                                "probs" : tmp_probs})

        self.update_faces_in_the_frame(tmp_face_in_the_frame)
        all_users = list(info["username"]for info in tmp_face_in_the_frame)
        if unknown_username in all_users:
            all_users.remove(unknown_username)
        
        if not self.debug_mode and len(all_users) > 0:
            tmp_lst = list(all_users)            
            username = tmp_lst[0]
            return username
        else:
            return None
        
    def update_faces_in_the_frame(self, faces_in_the_frame):
        self.faces_in_the_frame = faces_in_the_frame

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


