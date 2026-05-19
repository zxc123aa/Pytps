from zaber_motion.binary import Connection
from  zaber_motion import Units
com = 'com4'

connection =Connection.open_serial_port(com)

device_list = connection.detect_devices()
