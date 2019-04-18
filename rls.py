#!/usr/bin/env python3

import sys, os, time, random, argparse, signal



###### INFORMATIONS SUR LE BINOME (A COMPLETER  ###################

### ETUDIANT NUMERO 1

# NOM :
# PRENOM :
# NUM ETUDIANT


### ETUDIANT NUMERO 2

# NOM
# PRENOM
# NUM ETUDIANT



###### OPTIONS ET PARAMETRES DE LA LIGNE DE COMMANDE  ##############

FILENAME = ''   # le nom du fichier à rechercher
                # contient éventuellement des wildcards
DEBUG = False   # option -debug : pour activer les messages de debug
FIRST = False   # option -first-match : on s'arrête au premier fichier trouve
SERVER = False  # option -server




###### FONCTIONS AUXILIAIRES : NE PAS MODIFIER ####################

def debug(msg) :
    """affiche un message de debug sur la sortie d'erreur"""
    if DEBUG :
        sys.stderr.write("[{}] {}\n".format(os.getpid(), msg))
    

def change_dir(directory) :
    """change le répertoire dans lequel le processus s'exécute"""
    t = random.randint(1, 2)
    debug('entre dans le répertoire {} et dort {} sec'.format(directory, t))
    if DEBUG :
        time.sleep(t)
    os.chdir(directory)


def subdirs() :
    """renvoie la liste des sous-répertoires du répertoire courant"""
    return [x for x  in os.listdir() if os.path.isdir(x)]
    
def sys_exit(code) :
    debug('termine avec le code de sortie {}'.format(code))
    sys.exit(code)


def load_options() :
    """initialise les variables globales par rapport aux options saisies sur la ligne de commande"""
    global FILENAME, DEBUG, FIRST, SERVER
    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action='store_true', help='active le mode debug')
    parser.add_argument('-server', action='store_true', help='active le mode serveur')
    parser.add_argument('-first_match', action='store_true', help="s'arrête au premier fichier trouvé")
    parser.add_argument('FILENAME', type=str, nargs='?', help='le(s) fichier(s) à chercher')
    args = parser.parse_args()
    FILENAME = args.FILENAME
    SERVER = args.server
    DEBUG = args.debug
    FIRST = args.first_match
    if FILENAME == None and not SERVER :
        parser.error('FILENAME doit être spécifié')
        
    

####### FONCTIONS A MODIFIER  #####################################
    
def local_ls() :
    (read, write) = os.pipe()

    pid = os.fork()
    
    if pid == 0 :
        err = os.open('/dev/null',os.O_WRONLY)
        os.dup2(err,2)
        os.close(read)
        os.dup2(write,1)
        os.close(write)
        os.close(err)
        os.execv("/bin/sh", ["sh", "-c", "ls {}".format(FILENAME)])
    else :
        os.close(write)
        os.dup2(read,0)
        buff = os.read(read, 1)
        while (len(buff) > 0):
            os.write(1,buff)
            buff = os.read(read,1)
        os.close(read)
        L = [x for x in buff.decode().split('\n') if x != '']
        os.wait()
        return L
ListeFils = []

def handler(arg1,arg2) :
    for i in ListeFils :
        os.kill(i, signal.SIGUSR1)
    for j in ListeFils : 
        os.wait()
        sys_exit(2)

def handler2(signal,frame) :
    for i in ListeFils :
        os.kill(i, signal.SIGUSR1)
    for j in ListeFils : 
        os.wait()
    sys_exit(0)


def explorer(dirname,relative_path) :
    """explorateur"""
    change_dir(dirname)
    present = 0

    for x in local_ls() :
        print(os.path.join(relative_path, x))
        if FIRST :
            os.kill(os.getppid(),signal.SIGUSR2)
            sys_exit(0)
        present = 1
    Statut = list()
    for subdir in subdirs() :
        pid = os.fork()
        ListeFils.append(pid)
        if pid == 0 :
            ListeFils.clear()
            explorer(subdir, os.path.join(relative_path, subdir))
        else :
            Statut.append(os.wait()[1])
    Tout_processes = 0
    if all(Statut):
        Tout_processes = 2
    sys_exit(Tout_processes)

def main() :
    """fonction principale"""
    signal.signal(signal.SIGUSR1,handler)
    signal.signal(signal.SIGUSR2,handler2)
    load_options()
    explorer('.','')
    if(SERVER):
        launchServer()
    else:
        explorer('.','')
    
    
########################################################################## Partie Serveur 
def launchServer():
    global FILENAME
    host, port = '', 50000
    backlog, size = 5, 1024

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host,port))
    server.listen(5)
    input = [server,sys.stdin]
    running = 1
    while running:                                  #Ce code fonctionne comme l'exercice 1 du TD4
        inrdy,_,_ = select.select(input,[],[])      #Pour éviter de prendre tous les arguments de select.select en compte dans inrdy
        for s in inrdy:
            if s == server:
                client, address = server.accept()
                input.append(client)
                print("Un client est connecté")

            elif s == sys.stdin:                #Permet d'arrêter la boucle while mais aussi, permet d'éviter de mettre des choses dans l'entrée standard par inadvertance
                running = 0 

            else:
                data = s.recv(size)             #Ici on intercepte la requête de l'utilisateur
                if data:
                    FILENAME=data.decode()
                    (r,w) = os.pipe()
                    pid = os.fork()
                    if(pid == 0):               #Le fils doit juste écrire dans le pipe, on a pas besoin de r (on peut close)
                        os.close(r)
                        os.dup2(w,1)            #La on échange la sortie standard avec l'écriture dans le pipe
                        explorer('.','')        #On appelle, on lance donc la recherche du fichier 
                        os.close(1)             #On en a plus besoin, donc on ferme l'entrée standard
                        sys.exit(0)             #Quand un fils termine son travail il peut exit()
                    else:                       #Le pere doit juste lire, on peut close w
                        os.close(w)
                        lecteur=os.read(r,1024) #Cette partie permet au père d'envoyer les résultats obtenus part les fils au client.
                        while(len(lecteur) > 0):
                            s.send(lecteur)     #Ici on envoit le résultat obtenu au client puis on réinitialise lecteur.
                            lecteur=os.read(r,1024)
                else:
                    print("Un client s'est déconnecté")
                    s.close()
                    input.remove(s)
    server.close()


if __name__ == "__main__" :
    main()
