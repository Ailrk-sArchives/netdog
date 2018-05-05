"""
Server:
python netdoy.py -l -t xxx.xxx.xxx.xxx -p 1357
Client:
python netdoy.py -t xxx.xxx.xxx.xxx -p 1357 -e "sudo rm -rf /"
"""

import sys
import socket
import getopt
import subprocess
import threading

class TcpServer(object):
    """
    Tcp server to accept request and send back with response
    """
    def __init__(self, addr):
        (target, port) = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((target, port))
            self.socket.listen(5)
        except:
            print ("Error, unable to connect")
            sys.exit(1)

        self.server_loop()

    def server_loop(self, upload=None, execute=None, command=None):
        """create new threads to handle requests"""
        while True:
            conn, addr = self.socket.accept()
            conn_thread = threading.Thread(target=self.client_handler, args=(conn, upload,\
            execute, command))
            conn_thread.start()


    def client_handler(self, conn, upload=None, execute=None, command=None):
        """Services the server provides"""
        request = conn.recv(4096)

        # request in server act like a flag.``
        if execute != None:
            # grap the command part after $> in the request
            if request[:2] == "$>":
                request = request[2:]
                conn.send(self.__run__command(request))
                print ("executed")
                sys.exit(0)

        if upload:
            file_buffer = ""
            try:
                with open(upload, "wb") as f:
                    f.write(file_buffer)
                print ("File is wrote in to {}".format(upload))
            except:
                print ("Failing to write the file.")

        if command:
            while True:
                conn.send("<NetDog, forever be your dog:#>")
                cmd_buffer = ""
                #separate command apart by \n
                while "\n" not in cmd_buffer:
                    cmd_buffer += conn.recv(1024)

                conn.send(self.__run__command(cmd_buffer))


    def __run__command(self, command):
        """run command in a subprocess"""
        command = command.rstrip()
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, \
            shell=True)
        except:
            output = "Failed to execute the command\r\n"
        return output



class TcpClient(object):
    """
    Tcp client send resquest to ask for serveices
    """
    def __init__(self, addr):
        (target, port) = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((target, port))
        socket.socket()
        self.run()

    def run(self, upload="", execute=""):
        buffer = ""
        buffer = sys.stdin.read()
        try:
            # The client always send request first.
            if len(buffer):
                self.socket.send(buffer)
            # the main body of client. It do different works with different arguments
            while True:
                if len(upload):
                    self.__upload(upload)
                if len(execute):
                    self.__execute(execute)
                self.__interact()
        except:
            print ("[*] Failing to connect sever. Exiting")
            self.socket.close()
            sys.exit(0)

    def __interact(self):
        """ the basic funtion of client"""
        self.__client_receiver()
        self.__client_sender()

    def __upload(self, upload_destination):
        """once file is uploaded the program will exit"""
        try:
            with open(upload_destination, "r") as f:
                file_buffer = f.read()
                self.socket.send(file_buffer)
            print ("File accepted")
            sys.exit(0)
        except IOError:
            print ("[*] Failing to find file. Exiting")
            sys.exit(0)

    def __execute(self, execute):
        """
        after executed the instruction client will keep alive as normal mode
        Sever will parser the $> and execute comand after it
        """
        # trim the command
        execute = execute.rstrip()
        execute = "$>" + execute
        self.socket.send(execute)

    # Two funtions for basic data receive and send
    def __client_receiver(self):
            recv_len = 1
            response = ""
            # receiving data chunk by chunk
            while  recv_len:
                data = self.socket.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print (response,)
    def __client_sender(self):
            buffer = raw_input("");
            buffer += "\n"
            self.socket.send(buffer)


class NetDog(object):
    """
    Main entry of the program. Handle with cli argumennts
    different arguments have different effects in server and client
    """
    listen = False
    command = False
    upload = ""
    execute = ""
    target = ""
    port = 0

    def __init__(self):
        self.check_args()
        addr = (self.target, self.port)
        # Server mode
        if self.listen:
            server = TcpServer(addr)
            server.server_loop(self.upload, self.execute, self.command)

        if not self.listen:
            client = TcpClient(addr)
            client.run(self.upload, self.execute)

    def check_args(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hlce:u:t:p:", ["help", \
            "listen", "command", "execute", "upload", "target","port"])

            for o, a in opts:
                if o in ("-h", "--help"):
                    self.usage()
                elif o in ("-l", "--listen"):
                    self.listen = True
                elif o in ("-c", "--command"):
                    self.command = True
                elif o in ("-e", "--execute"):
                    # for client mode and server mode respectively
                    if self.listen == True:
                        self.execute = True
                    else:
                        self.execute = a
                elif o in ("-u", "--upload"):
                    self.execute = a
                elif o in ("-t", "--target"):
                    self.target = a
                elif o in ("-p", "--port"):
                    self.port = int(a)
                else:
                    assert False,"Unhandled argument"

        except getopt.GetoptError as e:
            print ("{}".format(str(e)))

    def usage():
        print ("Net Dog ----The most legitmate net tool faked from netcat")
        print ("Usage")
        print ("netdog -t <target_ip> -p <port> [--help-h][--command-c][--listen-l]\
        [--execute-e=<command_to_run>][--upload-u=<upload_destination>]")



if __name__ == '__main__':
    NetDog()
