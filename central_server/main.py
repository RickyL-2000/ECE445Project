from dynamics import Dynamics
from control import Control

dynamics = Dynamics()
light_config = {"lightA":
                    {"host":"192.168.31.7",
                     "port":12345},
                }
control = Control(dynamics, None, light_config)

control.run()
