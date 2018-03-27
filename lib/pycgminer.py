# Copyright (c) 2013 Thomas Sileo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
                sock.send(bytes(json.dumps(payload), 'utf-8'))
            received = self._receive(sock)
        except Exception as e:
            return dict({'STATUS': [{'STATUS': 'error', 'description': e}]})
        else:
            # the null byte makes json decoding unhappy
            # also add a comma on the output of the `stats` command by
            # replacing '}{' with '},{'
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


def get_summary(ip):
    cgminer = CgminerAPI(host=ip)
    output = cgminer.summary()
    output.update({"IP": ip})
    return dict(output)


def get_pools(ip):
    cgminer = CgminerAPI(host=ip)
    output = cgminer.pools()
    output.update({"IP": ip})
    return dict(output)


def get_stats(ip):
    cgminer = CgminerAPI(host=ip)
    output = cgminer.stats()
    output.update({"IP": ip})
    return dict(output)


if __name__ == '__main__':
    L3 = CgminerAPI(host='192.168.1.103')
    print(L3.stats())
    S7 = CgminerAPI(host='192.168.1.107')
    print(S7.stats())
    S9 = CgminerAPI(host='192.168.1.109')
    print(S9.stats())
