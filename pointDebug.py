from subprocess import Popen
from json import JSONDecoder
from random import random
import socket

def parse_config(config_file):
    print('Reading data from', config_file)
    with open(config_file) as open_file:
        clean_lines = [list(map(str.strip, line.split(':', maxsplit=1))) for line in open_file]
        config_data = {clean_line[0]:clean_line[1] for clean_line in clean_lines}
    return config_data


default_config_file = 'pointDebug.config'
default_config = parse_config(default_config_file)
octave = default_config['octave_path']

class Plot_Daemon:
    # start a plotting Daemon on port
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.decoder = JSONDecoder()

    def recieve(self, client):
        built_length = ''
        last_char = ''
        while not last_char == '\n':
            last_char = client.recv(1).decode()
            print(last_char)
            built_length += last_char
        message_length = int(built_length.strip())
        full_message = client.recv(message_length)
        return str(full_message.decode())

    def start(self, host, port):
        self.socket.bind((host, port))
        self.socket.listen(5)

        while True:
            (client_socket, address) = self.socket.accept()
            message = self.recieve(client_socket)
            client_socket.close()
            message_data = self.decoder.decode(message)
            points = message_data['point_groups']
            line_specs = message_data['line_specs']
            plot_points(points, line_specs)


# generate the octave code which plots the points, by default plot with red o
def gen_plot_code(point_lists, point_line_specs):
    code = "h=figure();hold();"
    for points, line_spec in zip(point_lists, point_line_specs):
        code += f"plot([{', '.join(map(lambda point : str(point['X']), points))}], [{', '.join(map(lambda point : str(point['Y']), points))}], '{line_spec}');"
    return code + 'axis(\'equal\');waitfor(h);'

def plot_points(points, line_specs):
    plot_command = gen_plot_code(points, line_specs)
    plot_file_name = str(random())+'plot_file.m'
    with open(plot_file_name, 'w') as plot_file:
        print(plot_command, file=plot_file)
    Popen([config_data['octave_path'], '--no-gui', plot_file_name])

if __name__ == "__main__":
    config_data = parse_config(default_config_file)
    daemon = Plot_Daemon()
    daemon.start('localhost', 8087)
