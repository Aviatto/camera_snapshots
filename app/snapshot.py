from datetime import datetime
from pathlib import Path
from PIL import Image

import requests
import argparse
import logging
import json
import io
import os


CONF_CAMERAS = 'cameras'

LOGGER_NAME = 'timelaps_logs'
LOG_FILE_NAME = 'timelaps_logs.log'

DATE_FORMAT = '%y_%m_%d__%H_%M_%S' 
SNAP_URL = 'http://{}.localdomain/snap.jpeg'
EMPTY_CONFIG = '{{"{}":[]}}'.format(CONF_CAMERAS)
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def make_dir(path):
    """
    Checks if 'path' exists and if not creates it

    :param path:    The path we want to make sure exists
    :type path:     str
    """
    if not os.path.exists(path):
        os.mkdir(path)


def get_logger(logger_name, log_path, level=logging.DEBUG):
    """
    Gets a logger for the current session

    :param txt:     The name of our logger
    :type txt:      Path the logs will be written to
    """
    logger = logging.getLogger(logger_name)  
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FORMAT)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def get_snap(ip):
    """
    Returns a snap from the camera in 'ip'

    :param ip:      The ip in which the camera is found
    :type ip:       str
    """
    global logger

    logger.info('trying getting the snapshot from {}'.format(ip))

    # Trying to retrieve the snapshot
    url = SNAP_URL.format(ip)
    try:
        logger.info('sending a get requests for {}'.format(url))
        jpeg = requests.get(url, timeout=5)
    except requests.exceptions.Timeout as e:
        logger.error('{} did not respond ):'.format(ip))
        return None
    except requests.exceptions.RequestException as e:
        logger.error('could not manage to get the snap...\n\t{}'.format(e))
        return None
    except Exception as e:
        logger.error('a new error had occurred!\n\t{}'.format(e))
        return None

    logger.info('got the snapshot with status code {}'.format(jpeg.status_code))

    # Checking if we indeed got the snapshot
    if jpeg.status_code == 200:
        jpeg_raw = jpeg.content
        jpeg_image = Image.open(io.BytesIO(jpeg_raw))

        return jpeg_image
    else:
        logger.error('got an unexpected error code {} instead of 200...'.format(jpeg.status_code))
        return None


def snap_cameras(cam_dict, root_dir):
    """
    Snapping every camera on the list

    :param cam_dict:    A dictionary of the cameras {<name> : <folder_to_save>}
    :type cam_dict:     dict {str : str}
    :param root_dir:    The directory in which we store our images
    :type root_dir:     str
    """
    global logger

    logger.info('going over all of the cameras getting some nice pics')

    for camera in cam_dict.keys():
        # The image that we want to save
        my_jpeg = get_snap(camera)

        if my_jpeg is None:
            return

        # The directory to which we shall save the image to
        my_dir = str(Path(root_dir) / Path(cam_dict[camera]))
        make_dir(my_dir)

        # The file name with the current date yo
        my_date_on_path = datetime.now().strftime(DATE_FORMAT)
        my_file = '{}_{}.jpeg'.format(cam_dict[camera], my_date_on_path)

        # The full path!
        my_path = str(Path(my_dir) / Path(my_file))
        my_jpeg.save(my_path)

# config_folder_name = 'config'
# config_file_name = 'cameras.json'
# snaps_folder_name = 'snaps'

def get_parser():
    parser = argparse.ArgumentParser(description='Gets a snapshot from your cameras')
    
    parser.add_argument('--conf-folder-name',
                        help='The name of the folder in which the configuration will be saved',
                        default='config')
    
    parser.add_argument('--conf-file-name',
                        help='Name of the config file, assumes it is under the config folder',
                        default='cameras.json')
    
    parser.add_argument('--snap-folder-name',
                        help='The name of the folder our snapshots will be saved',
                        default='snaps')

    return parser

def main():
    global logger

    parser = get_parser()
    args = parser.parse_args()
    config_folder_name, config_file_name, snaps_folder_name = (
        args.conf_folder_name,
        args.conf_file_name,
        args.snap_folder_name,
    )

    config_folder = str((Path(__file__).parent / Path(config_folder_name)).resolve())
    snaps_folder = str((Path(config_folder) / Path(snaps_folder_name)).resolve())
    config_file_path = str((Path(config_folder) / Path(config_file_name)).resolve())
    log_file_path = str((Path(config_folder) / Path(LOG_FILE_NAME)).resolve())

    # Asserting the paths we rely on exists
    assert Path(log_file_path).parent.exists(), 'log directory {} does not exists'.format(Path(log_file_path).parent)
    assert Path(config_folder).exists(), 'config dir {} does not exists'.format(config_folder)
    assert Path(snaps_folder).exists(), 'snapshot dir {} does not exists'.format(snaps_folder)

    logger = get_logger(LOGGER_NAME, log_file_path)
    logger.info('started running')
    logger.debug('config folder: {}'.format(config_folder))
    logger.debug('snaps folder: {}'.format(snaps_folder))
    logger.debug('config file: {}'.format(config_file_path))
    logger.debug('log file path: {}'.format(log_file_path))

    # Creating an empty config file if not exists
    if not Path(config_file_path).exists():
        logger.debug('config file does not exists so creating an empty one')
        with open(config_file_path, 'w') as f:
            json.dump(json.loads(EMPTY_CONFIG), f)
        logger.warning('created an empty config file, please fill it!')
    
    # Getting the cameras from the config
    with open(config_file_path, 'r') as f:
        conf = json.loads(f.read())

    assert CONF_CAMERAS in conf, 'could not find "{}" in the config file'.format(CONF_CAMERAS)
    
    cameras_dict = {}
    for i in conf[CONF_CAMERAS]:
        cameras_dict.update(i)

    if not cameras_dict:
        logger.warning('there are no cameras in the configuration')

    snap_cameras(cameras_dict, snaps_folder)
    logger.info('done!')


if __name__ == '__main__':
    main()
