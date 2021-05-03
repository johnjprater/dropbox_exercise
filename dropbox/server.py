''' A simple server which receives any change from its client '''
import os
from os.path import isdir, isfile, join
from argparse import ArgumentParser
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import logging
import json
import shutil


PORT = 8000
LOGGER = logging.getLogger('server')


parser = ArgumentParser(description=__doc__)
parser.add_argument('destination_dir', help='The destination directory')


class CustomHandler(BaseHTTPRequestHandler):
    ''' A dumb server which blindly uploads files from post requests '''

    def _set_response(self, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Let the client know what's in the server '''
        response_data = {        
            filename: os.stat(join(self.server.destination_dir, filename)).st_mtime
            for filename in os.listdir(self.server.destination_dir)
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode(encoding='utf_8'))

    def do_POST(self):
        ''' Upload a file to the dst dir or delete a file in the dst dir '''
        command = self.path
        if command == '/upload':
            assert self.headers['content-type']
            self.upload_file()
        elif command == '/delete':
            data_length = int(self.headers['Content-Length'])
            files_to_delete = json.loads(self.rfile.read(data_length))
            for filename in files_to_delete:
                file_path = os.path.join(self.server.destination_dir, filename)
                if isfile(file_path):
                    LOGGER.info(f'Deleting {filename}')
                    os.remove(file_path)
                else:
                    LOGGER.warning(f'Could not find {file_path}')
        elif command == '/duplicate':
            data_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(data_length))
            file_to_copy, new_name = data
            shutil.copy(
                join(self.server.destination_dir, file_to_copy),
                join(self.server.destination_dir, new_name)
            )
        else:
            self._set_response(400)
        self._set_response(200)

    def upload_file(self):
        '''
            At this point I realise I should probably have used flask or something similar.
            Taken from https://gist.github.com/touilleMan/eb02ea40b93e52604938 and hacked down a bit
        '''
        boundary = self.headers['content-type'].split("=")[1].encode()
        remaining_bytes = int(self.headers['content-length'])
        
        line = self.rfile.readline() # boundary
        remaining_bytes -= len(line)
        
        line = self.rfile.readline() # details
        filename = re.findall(
            r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())[0]
        remaining_bytes -= len(line)

        line = self.rfile.readline() # space
        remaining_bytes -= len(line)
        
        LOGGER.info(f'Uploading {filename}')
        with open(join(self.server.destination_dir, filename), 'wb') as output_file:
            boundary = self.headers['content-type'].split("=")[1].encode()
            preline = self.rfile.readline()
            remaining_bytes -= len(preline)
            while remaining_bytes > 0:
                line = self.rfile.readline()
                remaining_bytes -= len(line)
                if boundary in line:  # got to the end
                    preline = preline[0:-1]
                    if preline.endswith(b'\r'):
                        preline = preline[0:-1]
                    output_file.write(preline)
                    output_file.close()
                    return (True, f"File '{filename}' uploaded successfully!")
                else:
                    output_file.write(preline)
                    preline = line


if __name__ == '__main__':
    args = parser.parse_args()
    dst_dir = args.destination_dir
    assert isdir(dst_dir), 'The supplied argument is not a directory'
    with HTTPServer(("", PORT), CustomHandler) as httpd:
        httpd.destination_dir = dst_dir
        LOGGER.info(f'Server started at localhost:{PORT}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        LOGGER.info('Stopping server...\n')
