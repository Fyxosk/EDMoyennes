# Il faut mettre son login + mdp ici
EDLogin = "login"
EDMdp = "mdp"


from prettytable import PrettyTable
import requests
import json
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def connection(login, mdp):
    "Authentification a écoleDirecte, retourne le token et l'id"
    header = {'user-agent': 'EDELEVE MOBILE'}
    loginurl = 'http://vmws11.ecoledirecte.com/v3/login.awp?verbe=post'
    logindata = 'data={"identifiant" : "' + login +'","motdepasse" : "' + mdp + '"}'
    loginreq = requests.post(loginurl, data=logindata, headers=header)
    login_parsed = loginreq.json()
    if login_parsed['code'] != 200:
        #Si il y a une erreur quelconque
        print(login_parsed['message'])
        return False, 0, 0
    #Si il y en a pas
    token = login_parsed['token']
    login_id = str(login_parsed['data']['accounts'][0]['id'])
    return True, token, login_id

def notes(token, login_id):
    "Récupére les notes et retourne le JSON qu'envoie ED"
    header = {'user-agent': 'EDELEVE MOBILE'}
    noteurl = 'http://vmws11.ecoledirecte.com/v3/eleves/' + login_id + '/notes.awp?verbe=get'
    notedata = 'data={"token" : "' + token + '"}'
    notereq = requests.post(noteurl, data=notedata, headers=header)
    note_parsed = notereq.json()
    if note_parsed['code'] != 200:
        #Si il y a une erreur quelconque
        return False, 0
    #Si il y en a pas
    return True, note_parsed

def choixPeriode(notesjson):
    "Affiche une liste des trimestres et demande a l'utilisateur celle qui veut consulter, retourne je json du trimestre en question"
    i = 0
    for periode in notesjson['data']['periodes']:
    	i += 1
    	print (str(i) + " : " + periode['periode'])
    id_trim = int(input("Veuillez entrer le numéro du trimestre a consulter [" + str(i) + "] : ") or i) # Valeur par défaut i
    trim = notesjson['data']['periodes'][id_trim - 1] # Le compte commence a 0 donc i - 1
    return trim

def afficherMoyennes(trim):
    tableau = PrettyTable(["Matiere(coef)", "rang", "Moyenne", "Moyenne Classe", "Moyenne min", "Moyenne max"])
    for matiere in trim['ensembleMatieres']['disciplines']:
    	if matiere['codeMatiere'] != "":
    		tableau.add_row([matiere['discipline'] + "(" +  str(matiere['coef']) + ")", matiere['rang'] , matiere['moyenne'], matiere['moyenneClasse'], matiere['moyenneMin'],matiere['moyenneMax']])
    	else:
    		tableau.add_row([bcolors.HEADER  + matiere['discipline'], matiere['rang'] , matiere['moyenne'], matiere['moyenneClasse'], matiere['moyenneMin'],matiere['moyenneMax'] + bcolors.ENDC])
    tableau.add_row(["Général", "/", trim['ensembleMatieres']['moyenneGenerale'], trim['ensembleMatieres']['moyenneClasse'], trim['ensembleMatieres']['moyenneMin'], trim['ensembleMatieres']['moyenneMax']])
    print(tableau)
    print("Moyennes calculées le " + trim['ensembleMatieres']['dateCalcul'])

print("Bienvenue sur EcoleIndirecte, chargement...", end="")

succes, token, login_id = connection(EDLogin, EDMdp)
if(not succes):
    print("Une erreur est survenue")
    sys.exit(1)

succes, notesjson = notes(token, login_id)
if(not succes):
    print("Une erreur est survenue")
    sys.exit(1)

print("OK")

trim = choixPeriode(notesjson)

afficherMoyennes(trim)

print("Appuyez entrée pour quiter")
input()
