from typing import *

import fastapi as f

from amisHelper import startAmis

app=f.FastAPI()
startAmis(app,"/amis/set")
