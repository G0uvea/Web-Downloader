from pathlib import Path

# WINDOW VARIABLE
WINDOW_TITLE = "Youtube Downloader 1.1"
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 130
# WINDOW_HEIGHT = 170
WINDOW_ICON = Path(__file__).parent.parent / "assets" / "icon.ico"

# POSITIONS
STATUS_LABEL_POS = {"x": 215, "y": 80, "anchor": "n"} # mensagem de erro etc...
URL_ENTRY_POS = {"x": 150, "y": 0, "anchor": "n"}
SELECT_FOLDER_POS = {"x": 150, "y": 40, "anchor": "n"}
VIDEO_RES_POS = {"x": 370, "y": 0, "anchor": "n"}
DOWNLOAD_BTN_POS = {"x": 370, "y": 40, "anchor": "n"}
DOWNLOAD_PROGRESS_POS = {"x": 215, "y": 80, "anchor": "n"}

# CONFIG FILE FOLDER
USER_DOCUMENTS = Path.home() / "Documents"
APP_FOLDER = USER_DOCUMENTS / "Youtube Downloader"
CONFIG_FILE =  APP_FOLDER / "config.json"
DOWNLOAD_FOLDER = ""

# TEXT COLORS
NORMAL_COLOR = "#fff"
ERROR_COLOR = "#db1212"
SUCESS_COLOR = "#0ab20b"
WAITING_COLOR = "#dadd15"