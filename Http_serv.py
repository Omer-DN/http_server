
# Author: Omer dayan - 312409386

import socket
import os

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1

DEFAULT_URL = "\index.html"
VERSION_OF_HTTP = "HTTP/1.1 "
WEBROOT_LOCATION = r'C:\Networks\webroot\{}'
CONTENT_LENGTH = 'Content-Length: {}\r\n'
FORBIDDEN_LIST = [r'\answer2.7.txt', r'\my_photo.png']
REDIRECTION_DICTIONARY = {r'\from_page.html': 'to_page.html'}


def get_file_data(filename):
    """ Get data from file """
    with open(filename, 'rb') as read_file:
        data = read_file.read()
    return data


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""

    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    if resource == '':
        url = DEFAULT_URL
    else:
        url = resource
    # Handling special cases
    if url in REDIRECTION_DICTIONARY:
        http_rsp = (VERSION_OF_HTTP + "302 Found\r\nLocation: {}\r\n\r\n".format(REDIRECTION_DICTIONARY[url]))
        client_socket.send(http_rsp.encode())

    elif url in FORBIDDEN_LIST:
        http_rsp = (VERSION_OF_HTTP + "403 Forbidden\r\n\r\n")
        client_socket.send(http_rsp.encode())

    elif not os.path.isfile(WEBROOT_LOCATION.format(url)):
        http_rsp = (VERSION_OF_HTTP + "404 Not Found\r\n\r\n")
        client_socket.send(http_rsp.encode())

        # When the case is normal
    else:
        file_type = url.split('.')[1]
        file_size = os.path.getsize(WEBROOT_LOCATION.format(url))
        content_length = CONTENT_LENGTH.format(file_size)
        http_type = ''

        if file_type == 'html' or file_type == 'txt':
            http_type = 'Content-Type: text/html; charset=utf-8\r\n\r\n'
        elif file_type == 'jpg':
            http_type = 'Content-Type: image/jpeg\r\n\r\n'
        elif file_type == 'css':
            http_type = 'Content-Type: text/css\r\n\r\n'
        elif file_type == 'js':
            http_type = 'Content-Type:: text/javascript; charset=UTF-8\r\n\r\n'
        elif file_type == 'ico':
            http_type = 'Content-Type: image/vnd.microsoft.icon\r\n\r\n'

        http_response = (VERSION_OF_HTTP + "200 OK\r\n" + content_length + http_type).encode()
        file_name = WEBROOT_LOCATION.format(url)
        #  read the data from the file using the function: get_file_data
        data = get_file_data(file_name)
        http_rsp = http_response + data
        client_socket.send(http_rsp)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    first_line_header = request.split('\n')
    list_first_line = first_line_header[0].split(' ')

    if list_first_line[0] == 'GET' and list_first_line[1] == "/":  # Home page
        return True, ''

    list_first_line[1] = list_first_line[1].replace('/', '\\')

    if list_first_line[0] == 'GET' and list_first_line[2] == 'HTTP/1.1\r':
        return True, list_first_line[1]
    else:
        return False, "Error"


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')

    while True:
        try:
            client_request = client_socket.recv(1024).decode()
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket)
                break
            else:
                print('Error: Not a valid HTTP request')
                http_response = (VERSION_OF_HTTP + "500 internal server error\r\n\r\n").encode()  # 500 code
                client_socket.send(http_response)
                break
        except Exception:
            break
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
