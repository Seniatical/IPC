"""
MIT License

Copyright (c) 2021 Seniatical

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class ServerStartupError(Exception):
    r"""
    Raised when the server side fails to startup;

    Causes:
    Host or Port are invalid
    Host & Port are occupied
    """

class ServerNotRunningError(Exception):
    r"""
    Raised when you try preform an action which involves a server
    Without the actual server running
    """

class DuplicateCall(Exception):
    r"""
    Raised when you try to assign a new register call when the existing name already exists

    e.g.

    @client.on_call('test')
    def my_test():
        return 'hi'

    test is now a registered event
    but if you were to re-assign it to another function
    it will raise this error
    """

class SendingError(Exception):
    r"""
    Raised when the web/app cant send a packet

    Usually due to TypeErrors and Packet size being too large
    If you want to send a large amount of data use `client.send_file(file_path | bytes | contents | json)`
    """
