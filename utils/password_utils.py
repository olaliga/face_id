
import keyring
from utils.common_utils import get_default_logger
# TODO login other applications


class PassWordManager:
    def __init__(self, userid, logger = get_default_logger()):
        self.userid = userid
        self.servicename = "system"
        self.logger = logger
        
    def set_password(self):
        password = input("Please enter the password for system login :")
        keyring.set_password(self.servicename, self.userid, password)

    def get_password(self):
        self.logger.info(f"servicename : {self.servicename}, userid : {self.userid}")
        return keyring.get_password(self.servicename, self.userid)



