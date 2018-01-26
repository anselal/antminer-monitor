import socket
import json


class CgminerAPI(object):
    """ Cgminer RPC API wrapper. """

    def __init__(self, host='localhost', port=4028, payload_command='command'):
        self.data = {}
        self.host = host
        self.port = port
        self.payload_command = payload_command

    def command(self, command, arg=None):
        """ Initialize a socket connection,
        send a command (a json encoded dict) and
        receive the response (and decode it).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            sock.connect((self.host, self.port))

            # payload = {"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}
            payload = {self.payload_command: command}

            if arg is not None:
                # Parameter must be converted to basestring (no int)
                payload.update({'parameter': str(arg)})

            message = json.dumps(payload)

            sock.send(message.encode())
            response = str(sock.recv(65536).decode())

            # Bug in Antminer JSON
            # also add a comma on the output of the `stats` command by replacing '}{' with '},{'
            if response.find("\"}{\"STATS\":"):
                response = response.replace("\"}{\"STATS\":","\"},{\"STATS\":",1)

            # Another bug in Antminer JSON
            # the null byte makes json decoding unhappy
            # TODO - test for NULL byte at end
            if (response.endswith("}") == False):
                response = response[:-1]

            received = json.loads(response)

        except Exception as e:
            return dict({'STATUS': [{'STATUS': 'error', 'description': str(e)}]})
        else:
            return received
        finally:
            # sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def _receive(self, sock, size=4096):
        msg = ''
        while 1:
            chunk = sock.recv(size)
            if chunk:
                msg += chunk
            else:
                # end of message
                break
        return msg

    def __getattr__(self, attr):
        """ Allow us to make command calling methods.

        >>> cgminer = CgminerAPI()
        >>> cgminer.summary()

        """

        def out(arg=None):
            return self.command(attr, arg)

        return out

