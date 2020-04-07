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

def adapt_to_server(cli, state, modif, turn, useful_stuff1, useful_stuff2):
    if cli.info_rcvd != None :
        state = cli.info_rcvd.get("state")
        modif = cli.info_rcvd.get("modif")
        turn = cli.info_rcvd.get("turn")
        useful_stuff1 = cli.info_rcvd.get("useful stuff 1")
        useful_stuff2 = cli.info_rcvd.get("useful stuff 2")
        cli.info_rcvd = None
    return state, modif, turn, useful_stuff1, useful_stuff2

def adapt_to_client(serv, state, modif, turn, useful_stuff1, useful_stuff2):
    if serv.info_rcvd != None :
        state = serv.info_rcvd.get("state")
        modif = serv.info_rcvd.get("modif")
        turn = serv.info_rcvd.get("turn")
        useful_stuff1 = serv.info_rcvd.get("useful stuff 1")
        useful_stuff2 = serv.info_rcvd.get("useful stuff 2")
        serv.info_rcvd = None
    return state, modif, turn, useful_stuff1, useful_stuff2

def sending_and_receiving(serv, cli, info_sent, info, state, modif, turn, useful_stuff1, useful_stuff2):
    #si c'est le serveur
    if (serv != None) & (state == "units placement"):
        useful_stuff1 = False

    if (serv != None) & (cli == None) & (not info_sent): #Si t'es le serveur et que t'envoies
        if serv.conn != None :
            serv.send_obj(serv.conn, info)

    if (serv != None) & (cli == None) : #Si t'es serveur et que tu reçois
        state, modif, turn, useful_stuff1, useful_stuff2 = adapt_to_client(serv, state, modif, turn, useful_stuff1, useful_stuff2)

    #si c'est le client
    if (serv == None) & (cli != None) & (not info_sent) & (state != "entry") & (state != "waiting for connexion") & (state != "connexion established"): #Si t'es le client et que t'envoies
        cli.send_obj(info)
    
    if (serv == None) & (cli != None): #Si t'es client et que tu reçois
        state, modif, turn, useful_stuff1, useful_stuff2 = adapt_to_server(cli, state, modif, turn, useful_stuff1, useful_stuff2)

    info_sent = True

    return info_sent, state, modif, turn, useful_stuff1, useful_stuff2