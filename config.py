from fastapi.templating import Jinja2Templates

UPLOAD_DIR = "static/uploads"
APP_NAME = "The Vanity Edit"
APP_VERSION = "1.0.0"

templates = Jinja2Templates(directory="templates")
