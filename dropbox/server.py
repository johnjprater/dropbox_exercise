''' TODO '''
import os
from os.path import isdir
from argparse import ArgumentParser
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import logging
import json


PORT = 8000
LOGGER = logging.getLogger('server')


parser = ArgumentParser(description= 'A simple server which receives any change from its client')
parser.add_argument('destination_dir', help='The destination directory')


class CustomHandler(BaseHTTPRequestHandler):
    ''' A dumb server which blindly uploads files from post requests '''

    def _set_response(self, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Let the client know what's in the server '''
        response_data = os.listdir(self.server.destination_dir)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode(encoding='utf_8'))

    def do_POST(self):
        ''' Blindly upload a file do the destination directory '''
        filename = self.path
        if filename == '/':
            LOGGER.info('No file to upload')
        elif self.headers['content-type']:
            LOGGER.info(f'Uploading {filename}')
            self.write_file(filename)
        else:
            LOGGER.info(f'Deleting {filename}')
            os.remove(f'{self.server.destination_dir}{filename}')
        self._set_response(200)

    def write_file(self, filename):
        '''
            At this point I realise I should probably have used flask or something similar.
            Taken from https://gist.github.com/touilleMan/eb02ea40b93e52604938 and hacked down a bit
        '''
        boundary = self.headers['content-type'].split("=")[1].encode()
        remaining_bytes = int(self.headers['content-length'])
        # boundary
        line = self.rfile.readline()
        remaining_bytes -= len(line)
        # details
        line = self.rfile.readline()
        remaining_bytes -= len(line)
        # space
        line = self.rfile.readline()
        remaining_bytes -= len(line)

        with open(f'{self.server.destination_dir}{filename}', 'wb') as output_file:
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
