from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

mail = Mail()
cors = CORS()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
