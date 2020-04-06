import client
import server
import threading
import socket

host = socket.gethostbyname(socket.gethostname())
port = 5555

def launch_server(state):
    serv = server.Server()
    serv.create_server(host, port)
    threading.Thread(target=serv.wait_for_a_connection).start()
    return serv

def adapt_to_server(cli, state, modif, turn, useful_stuff):
    if cli.info_rcvd != None :
        state = cli.info_rcvd.get(1)
        modif = cli.info_rcvd.get(2)
        turn = cli.info_rcvd.get(3)
        useful_stuff = cli.info_rcvd.get(4)
        cli.info_rcvd = None
    return state, modif, turn, useful_stuff

def adapt_to_client(serv, state, modif, turn, useful_stuff):
    if serv.info_rcvd != None :
        state = serv.info_rcvd.get(1)
        modif = serv.info_rcvd.get(2)
        turn = serv.info_rcvd.get(3)
        useful_stuff = serv.info_rcvd.get(4)
        serv.info_rcvd = None
    return state, modif, turn, useful_stuff

def sending_and_receiving(serv, cli, info_sent, info, state, modif, turn, useful_stuff):
    #si c'est le serveur
    if (serv != None) & (state == "units placement"):
        useful_stuff = False

    if (serv != None) & (cli == None) & (not info_sent): #Si t'es le serveur et que t'envoies
        if serv.conn != None :
            serv.send_obj(serv.conn, info)

    if (serv != None) & (cli == None) : #Si t'es serveur et que tu reçois
        state, modif, turn, useful_stuff = adapt_to_client(serv, state, modif, turn, useful_stuff)

    #si c'est le client
    if (serv == None) & (cli != None) & (not info_sent) & (state != "entry") & (state != "waiting for connexion") & (state != "connexion established"): #Si t'es le client et que t'envoies
        cli.send_obj(info)
    
    if (serv == None) & (cli != None): #Si t'es client et que tu reçois
        state, modif, turn, useful_stuff = adapt_to_server(cli, state, modif, turn, useful_stuff)

    info_sent = True

    return info_sent, state, modif, turn, useful_stuff