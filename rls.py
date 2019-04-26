#!/usr/bin/env python3

import sys, os, time, random, argparse, signal, socket, select



###### INFORMATIONS SUR LE BINOME (A COMPLETER  ###################

### ETUDIANT NUMERO 1

# NOM : Kouyoumdjian
# PRENOM : Pierre
# NUM ETUDIANT : 21705950


### ETUDIANT NUMERO 2

# NOM : Picard
# PRENOM : Tristan
# NUM ETUDIANT : 21704153



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
    (read, write) = os.pipe() #On créer un pipe pour remplacer la sortie et l'entrée standard

    pid = os.fork() #On fork pour pourvoir lancer un execv en arrière plan 
    
    if pid == 0 :
        err = os.open('/dev/null',os.O_WRONLY) 
        os.dup2(err,2)   #On redirige la sortie erreur vers /dev/null
        os.close(read)  #On écrit donc on ferme read
        os.dup2(write,1)  #On remplace la sortie standard par le write 
        os.close(write) 
        os.close(err)
        os.execv("/bin/sh", ["sh", "-c", "ls {}".format(FILENAME)]) #On éxécute sh -c ls  dans un sous terminal
    else :
        os.close(write) 
        os.wait()
        buff = os.read(read, 10) #On stock le début de la sortie du pipe dans une variable
        while (len(buff)>0): #On stock jusqu'à ce que le pipe soit vide
            os.write(1,buff)
            buff = os.read(read,10)
        os.close(read)
        L = [x for x in buff.decode().split('\n') if x != ''] #On remet tout en str (car dans le pipe c'est en bits, et on sépare
        return L
    
ListeFils = [] #Liste global pour stocker le pid des fils 

def handler(arg1,arg2) : #Fonction en réception d'un signal quand ce n'est pas la racine
    for i in ListeFils : #On parcourt ListeFils et on os.kill pour chaque 
        os.kill(i, signal.SIGUSR1)
    for j in ListeFils : #On attend chaque fils puis on arrête le processus
        os.wait()
        sys_exit(2)

def handler2(signal,frame) : #Pareil que le handler mais seulement pour le processus racine
    for i in ListeFils :
        os.kill(i, signal.SIGUSR1)
    for j in ListeFils : 
        os.wait()
    sys_exit(2)

def explorer(dirname,relative_path) :
    """explorateur"""
    change_dir(dirname)

    for x in local_ls() : #Quand on a trouvé le fichier on print son chemin
        print(os.path.join(relative_path, x))
        if FIRST : #Si first_match est activé alors on envoi un signal au processus racine et on arrête ce processus
            os.kill(os.getppid(),signal.SIGUSR2)
            sys_exit(0)
    for subdir in subdirs() :
        pid = os.fork() #Pour chaque dossier on créer un processus qui l'explorera
        ListeFils.append(pid) #On ajoute son pid à ListeFils
        if pid == 0 :
            explorer(subdir, os.path.join(relative_path, subdir)) #Le fils explore un sous fichier
    statut_processes = 0 #On stock le statut du processus fils
    for subdir in subdirs():
        (pid, statut) = os.waitpid(-1, 0)
        if os.WIFEXITED(statut):
            statut_processes = os.WEXITSTATUS(statut)
        else:
            statut_processes = os.WEXITSTATUS(statut)
    sys_exit(statut_processes) #On fini avec le code récupérer dans la boucle juste au dessus
######################################################################### Partie Serveur 
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
                        os.close(1)             #On en a plus besoin, donc on ferme la sortie standard
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

def main() :
    """fonction principale"""
    signal.signal(signal.SIGUSR1,handler) #On attend les signals (les fils héritent de ces signal.signal
    signal.signal(signal.SIGUSR2,handler2)
    load_options()
    if(SERVER): #SI -server est en argument alors on lance le serveur sinon on lance direct l'exploreur 
        launchServer()
    else:
        explorer('.','')

if __name__ == "__main__" :
    main()
