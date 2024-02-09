import os
from face_id import FaceId
from utils.db_utils import create_new_user
from pathlib import Path
import argparse
import time
import pyautogui
from utils.common_utils import timing, log, get_default_logger

# TODO Params Parser
class FaceIdConfig:
    def __init__(self, task):
        self.task = task
        self.user_db_path = Path(__file__).parent/Path("user_db")

    def get_task(self):
        return self.task

    def get_user_db_path(self):
        return self.user_db_path


@log
@timing
def main(logger = get_default_logger()):
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Assign the task")
    args = parser.parse_args()
    logger.info("Task is : {args.task}")
    configs = FaceIdConfig(args.task)
    if configs.get_task() == "detection":
        logger.info(f"Init Face ID")
        faceid = FaceId(configs.get_user_db_path())        
        logger.info(f"face id detection")
        username = faceid.detect()
        if faceid.is_login(username):
            password = faceid.get_password(username)
            pyautogui.click()            
            os.system(f'osascript -e \'tell application "System Events" to keystroke "{password}"\'')
            pyautogui.press('enter')
    elif configs.get_task() == "create_user":
        create_new_user()
    else:
        print(f"error ")
        raise 

if __name__ == "__main__":
    main()
