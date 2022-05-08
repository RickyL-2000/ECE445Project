from control import Control
from dynamics import Dynamics
from utils.config import LIGHT_MOCK, LIGHT_PORT

dynamics = Dynamics()
light_config = {"lightB":
                    {"host":LIGHT_MOCK,
                     "port":LIGHT_PORT},
                }
control = Control(dynamics, None, light_config)

control.run()
