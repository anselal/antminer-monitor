import socket
import json
import sys


class CgminerAPI(object):
    """ Cgminer RPC API wrapper. """

    def __init__(self, host='localhost', port=4028):
        self.data = {}
        self.host = host
        self.port = port

    def command(self, command, arg=None):
        """ Initialize a socket connection,
        send a command (a json encoded dict) and
        receive the response (and decode it).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            sock.connect((self.host, self.port))
            payload = {"command": command}
            if arg is not None:
                # Parameter must be converted to basestring (no int)
                payload.update({'parameter': arg})

            if sys.version_info.major == 2:
                sock.send(json.dumps(payload))
            if sys.version_info.major == 3:
                sock.send(bytes(json.dumps(payload),'utf-8'))
            received = self._receive(sock)
        except Exception as e:
            return dict({'STATUS': [{'STATUS': 'error', 'description': e}]})
        else:
            # the null byte makes json decoding unhappy
            # also add a comma on the output of the `stats` command by replacing '}{' with '},{'
            return json.loads(received[:-1].replace('}{', '},{'))
        finally:
            # sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def _receive(self, sock, size=4096):
        msg = ''
        while 1:
            chunk = sock.recv(size)
            if chunk:
                if sys.version_info.major == 2:
                    msg += chunk
                if sys.version_info.major == 3:
                    msg += chunk.decode('utf-8')
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


if __name__ == '__main__':
    L3 = CgminerAPI(host='192.168.1.103')
    print(L3.stats())
    S7 = CgminerAPI(host='192.168.1.107')
    print(S7.stats())
    S9 = CgminerAPI(host='192.168.1.109')
    print(S9.stats())
