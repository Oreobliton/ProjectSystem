#!/usr/bin/env python3

import sys, os, time, random, argparse



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
    """renvoie la liste des fichiers du répertoire courant qui correspondent à FILENAME"""
    # A MODIFIER : lancer un sous-processus ls pour autoriser les wildcards dans FILENAME
    return [x for x in  os.listdir() if x == FILENAME]


def explorer(dirname,relative_path) :
    """explorateur"""
    change_dir(dirname)
    for x in local_ls() :
        print(os.path.join(relative_path, x))
    for subdir in subdirs() :
        explorer(subdir, os.path.join(relative_path, subdir))
        change_dir('..')


        
def main() :
    """fonction principale"""
    load_options()
    explorer('.','')

if __name__ == "__main__" :
    main()
