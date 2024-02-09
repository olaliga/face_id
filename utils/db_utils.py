from pathlib import Path
import os, shutil
import cv2

from utils.camara_utils import capture_img
from utils.password_utils import PassWordManager
import face_recognition
import numpy as np

from utils.common_utils import timing, log, get_default_logger


#####
class UserInfo():
    def __init__(self, username, user_db_path = "./user_db", logger = get_default_logger()): 
        self.logger = logger    
        self.username = username
        self.user_img_folder = Path(user_db_path)/Path(self.username)
        self.face_encodings_filename = "face_encoding_lst.npy"
        self.img_path_lst =  self.create_img_path_lst()
        self.password_manager = PassWordManager(username)
        self.face_encodings_lst = self.set_face_encodings() 
        
    def create_img_path_lst(self):
        return [ Path(self.user_img_folder)/Path(img_name) for img_name in os.listdir(self.user_img_folder)]

    def get_password(self):
        return self.password_manager.get_password()
        
    def cal_face_encodings(self):
        face_encodings = []
        for img_path in self.img_path_lst :
            if not img_path.name.startswith("."):
                user_image = face_recognition.load_image_file(img_path)
                face_locations = face_recognition.face_locations(user_image)
                user_face_encoding = face_recognition.face_encodings(user_image, face_locations)[0]
                face_encodings.append(user_face_encoding)

        return face_encodings

    def save_face_encodings_lst(self, face_encodings, filepath):
        np.save(filepath, face_encodings, allow_pickle=True)

    @timing
    def set_face_encodings(self):
        face_encodings_path = str( self.user_img_folder / Path(self.face_encodings_filename) )
        if self.is_face_encodings_saving(face_encodings_path):
            # read the face encodings in the db
            tmp_face_encodings = np.load(face_encodings_path, allow_pickle=True)
            face_encodings = list(tmp_face_encodings) # since np load will turn saving list into np array
        else:
            # if never have face encodings then calculate and save for next time readings
            face_encodings = self.cal_face_encodings()  
            self.save_face_encodings_lst(face_encodings, face_encodings_path)
        return face_encodings

    def is_face_encodings_saving(self, face_encodings_path):
        self.logger.info(f"face encodings filename : {Path(self.face_encodings_filename)}")
        if Path(face_encodings_path) in self.img_path_lst:
            return True
        return False

    def get_face_encodings(self):
        return self.face_encodings_lst



class UserDB():
    def __init__(self, user_db_path = "./user_db", logger = get_default_logger()):
        logger.info(f"access db root path {user_db_path}")
        self.logger = logger
        self.user_db_path = user_db_path
        self.user_db = self.create_user_db(user_db_path)
        
    def create_user_db(self, user_db_path):
        user_db = {}
        for __, username_dirs, __ in os.walk(user_db_path):
            for username in username_dirs:
                user_db.update({username : UserInfo(username, user_db_path)})

        return user_db

    def build_user(self, newusername):
        ### check username exists or not
        for username in list(self.user_db.keys()):
            if newusername == username :
                raise "Username exists in the database"
        ###TODO need to closer (future dev)

        # setting passwords
        password_manage = PassWordManager(newusername)
        password_manage.set_password()

        ### film 9 imgs and save to folder
        ###  \ | /
        ###  - x -
        ###  / | \
        newuser_img_folder = Path(self.user_db_path)/Path(newusername)
        os.makedirs(newuser_img_folder, exist_ok=False)

        try :
            for direction in ["right", "middle", "left"]:
                for direction2 in ["top", "", "button"]:
                    self.logger.info(f"Please look {direction} {direction2}")
                    imgname = f"{direction2}_{direction}.jpg"
                    capture_img(Path(newuser_img_folder)/Path(imgname))
        except : 
            shutil.rmtree(newuser_img_folder)
            raise "Error"

    def get_face_ecoding_dict(self):
        face_ecoding_dict = {}
        for username, user_info in self.user_db.items():
            face_ecoding_dict.update({username : user_info.get_face_encodings()})
        return face_ecoding_dict

    def __getitem__(self, key):
        return self.user_db[key]


def create_new_user():
    new_username = input("Please Input New User Name :")
    user_database = UserDB()
    user_database.build_user(new_username)


