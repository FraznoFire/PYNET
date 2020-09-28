# this will be both a client and server, and will allow people to view, create, deposit and withdraw from accounts. each user's data will be saved to an XML file

import socket
import threading
import os.path as Path
import xml.etree.ElementTree as xt
from time import sleep as snooze

""" Protocol Codes """
# 1 = no file available, please wait
# 3 = file available, sending..
# the above affects the behaviour of the client. e.g. when it gets "1" it will wait for the server to send "3", upon which it will display the received data.

""" Server Related Functions: """

AuthList = ["RandomDude", "Chinq", "admin"]
AuthPass = ["1234", "superpassword", "Secret"]
CLIENTS = {}
ACCOUNTS = {}
def Server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("[MAIN/INFO] setting up server...")
        s.bind(('0.0.0.0',6500))
        s.listen(3) # maybe 50 will allow up to 50 connections and stop the disconnect error? idk it seems to be the only thing
        print("[MAIN/INFO] server online! awaiting connection..")
        while True:
            conn, addr = s.accept()
            print("[MAIN/INFO] received connection from", addr)
            print("[MAIN/INFO] passing to a USER thread..")
            threading.Thread(target=Authenticate, args=(conn,addr, )).start()

def Authenticate(conn, address):
    print("[USER/INFO] Connection successfully transferred {0} to a USER Thread!".format(address))
    username = ""
    try:
        attemptedlogin = conn.recv(1024)
        attemptedlogindecoded = attemptedlogin.decode()
        attemptedloginsplit = attemptedlogindecoded.split(":")
        authenticated = False
        username = attemptedloginsplit[0]
        for i in range(0, len(AuthList), 1):
            if attemptedloginsplit[0] == AuthList[i]:
                if attemptedloginsplit[1] == AuthPass[i]:
                    alreadysignedin = username in CLIENTS.values()
                    if alreadysignedin == False:
                        CLIENTS[conn] = username
                        conn.sendall(b'Authed!')
                        authenticated = True
                        print("[USER/AUTH] connection {0} has successfully signed into account {1}".format(address, username))
                    else:
                        print("[USER/AUTH] ALERT {0} attempted to sign into account {1} which is already connected!".format(address, username))
                        conn.sendall(b'That user is already signed in!')
                else:
                    print("[USER/AUTH] ALERT {0} attempted to sign into account {1} with an incorrect password!".format(address, username))
        if authenticated == False:
            print("[USER/AUTH] ALERT {0} failed to Authenticate and the connection has been terminated".format(address))
            conn.sendall(b'Incorrect Username/Password')
            conn.close()
        else:
            yeamate(conn, address, username)
    except:
        print("[USER/INFO] lost connection to", address)
        if conn in CLIENTS.keys():
            if username in ACCOUNTS.keys():
                USERPATH = username + ".xml"
                USERDATA = '<?xml version="1.0"?>\n<data>\n<account Name="Savings" Balance="' + str(ACCOUNTS[username]) + '"/>\n</data>'
                USERFILE = open(USERPATH, "w")
                USERFILE.write(USERDATA)
                USERFILE.close()
                del ACCOUNTS[username]
                print("[USER/AUTH] {0} account data has been saved to non-volatile storage.".format(username))
            uname = CLIENTS[conn]
            del CLIENTS[conn]
            print("[USER/AUTH] {0} has been signed out successfully from {1}".format(uname, address))
    print("[USER/INFO] closing thread for connection to {0}.. goodbye".format(address))

def yeamate(conn, addr, username):
    USERPATH = username + ".xml"
    if Path.exists(USERPATH):
        print("[USER/INFO] " + username + " has an account! sending now..")
        conn.sendall(b"3")
        #snooze(1)
        xml_sp = xt.parse(USERPATH)
        xml_sp_root = xml_sp.getroot()
        for i in xml_sp_root.iter("account"):
            accountname = i.attrib["Name"]
            balance = i.attrib["Balance"]
            ACCOUNTS[username] = float(balance)
        
        USERDATA = accountname + ":" + balance
        conn.sendall(USERDATA.encode())
        print("[USER/INFO] " + username + " has been sent their information!")

    else:
        print("[USER/INFO] " + username + " does not currently have an account.. setting up now..")
        conn.sendall(b'1')
        xmlString = '<?xml version="1.0"?>\n<data>\n'
        xmlString += '<account Name="Savings" Balance="0"/>'
        xmlString += '\n</data>'
        USERFILE = open(USERPATH, "w")
        USERFILE.write(xmlString)
        USERFILE.close()
        #snooze(1)
        print("[USER/INFO] " + username + "'s account has been setup, re-running this function..")
        yeamate(conn, addr, username)

    raise Exception("Communication has ended..")




""" Client related functions: """

def Client():
    while True:
        HOSTIP = input("Please enter IP to connect to: ")
        PORTTHING = 6500
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("attempting to connect...")
            s.connect((HOSTIP, PORTTHING))
            print("connected!")
            attemptuser = input("Please enter your username: ")
            attemptpass = input("Please enter your password: ")
            attempt = attemptuser + ":" + attemptpass
            attemptbytes = str.encode(attempt)
            s.sendall(attemptbytes)
            reply = s.recv(1024).decode()
            print(reply)
            if reply == "Authed!":
                ClientNoises(s)
            else:
                break

def ClientNoises(conn):
    ServerMessage = conn.recv(1024).decode()
    if ServerMessage == "1":
        print("Server is setting up an account..")
        ServerMessage = conn.recv(1024).decode()
        if ServerMessage == "3":
            LoggedInNoises(conn)
    else:
        LoggedInNoises(conn)
            
def LoggedInNoises(conn):
    print("Receiving Account information from server..")
    ServerMessage = conn.recv(1024).decode()
    SplitMessage = ServerMessage.split(":")
    AccountName = SplitMessage[0]
    AccountBalance = SplitMessage[1]
    print("Account: {0} has a balance of: ${1}".format(AccountName,AccountBalance))



""" Main Loop """

while True:
    print("==========================")
    print("is this a server or client?")
    print("1) Server")
    print("2) Client")
    SorC = input(": ")
    if SorC == "1":
        Server()
    elif SorC == "2":
        Client()
    else:
        print("Please enter a correct input")
