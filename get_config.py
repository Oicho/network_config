import netmiko
import time

# Dictionary to map "show run" command to different type of devices
SHOW_RUN_DIC =  {
    'hp_comware': 'display current-configuration',
    'hp_procurve': 'show run',
    'ciscio_ios': 'show run'
}

class NetworkDevice:
    def __init__(self, ip, username, password, type=None):
        self.ip = ip
        self.username = username
        self.password = password
        self.type = type
        self.net_connect = None

    def check_connection(self):
        if not self.net_connect:
            self.net_connect = netmiko.ConnectHandler(device_type=self.type, ip=self.ip, username=self.username, password=self.password)

    def get_config(self):
        self.check_connection()

        # TODO: change 'display cur' depending on the type of network device
        return self.net_connect.send_command(SHOW_RUN_DIC[self.type])

    def send_config_to_file(self, filename):
        try:
            self.check_connection()
            configfile = open(filename, 'w')
            config = self.net_connect.send_command(SHOW_RUN_DIC[self.type])
            configfile.write(config)
        except (OSError, IOError) as e:
            print('Could not open file. ' + str(e))
        except Exception as e:
            print('Error. ' + str(e))


def read_inventory(filename):
    network_devices = []

    inventory = open(filename, 'r')
    for line in inventory.readlines():
        if line.startswith('#'):
            continue
        line_array = line.strip().split((','))
        device = NetworkDevice(line_array[0], line_array[1], line_array[2], line_array[3])
        network_devices.append(device)

    return network_devices

if __name__ == '__main__':
    network_devices = read_inventory('test.csv')

    for device in network_devices:
        print(device.get_config())

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        device.send_config_to_file('tmp/' + device.ip + '_' + timestamp + '.cfg')