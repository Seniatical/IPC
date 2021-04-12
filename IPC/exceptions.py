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

def SendingError(Exception):
    r"""
    Raised when the web/app cant send a packet

    Usually due to TypeErrors and Packet size being too large
    If you want to send a large amount of data use `client.send_file(file_path | bytes | contents | json)`
    """
