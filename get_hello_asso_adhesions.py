# getHelloAssoAdhesion.py
# Python3
# Auteur : Fafadji GNOFAME
# Date : 25 Fevrier 2018
# Version : 0.3
# Description :  recupere l'ensemble des adherents helloAsso et les ecrit dans un fichier csv

import requests, csv, sys, argparse

def get_hello_asso_adhesion(id_campagne, hello_asso_user, hello_asso_pass):

    results_per_page = 100
    # on prend les adhesions a partir d'une date donnee
    createdFrom = "2017-04-01T00:00:00"
    
    # id de la campagne concerne
    
    helloAsso_url_params = "type=SUBSCRIPTION&results_per_page="+str(results_per_page)+"&from="+createdFrom
    helloAsso_url_adhesions = "https://api.helloasso.com/v3/campaigns/"+id_campagne+"/actions.json?"+helloAsso_url_params
    
    
    # Premiere requete pour determinier le nombre de page sur lequel on va boucler
    r = requests.get(helloAsso_url_adhesions+'&page=1', auth=(hello_asso_user, hello_asso_pass))
    if r.status_code != 200:
        print("erreur de requetage. Code de reponse http : "+str(r.status_code))
        sys.exit(2)
              
    r_json = r.json()
    
    pagination = r_json.get("pagination")
    nombre_page = pagination.get("max_page")
    
    page_courante = 0
    nombre_adherents = 0
    
    # On ouvre un fichier csv
    with open('adherents.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='|', quotechar=' ', quoting=csv.QUOTE_MINIMAL)   
        
        # On ecrit la ligne d'entete dans le fichier csv
        csv_line_header =  ["id", "Date Adhesion" , "Nom", "Prenom", "email", "detection doublon" ,  "Adhesion", "Telephone", "Adresse", "Ville", "Code Postal"]       
        csv_writer.writerow(csv_line_header)    
        
        # On boucle sur les pages retournees par helloAsso
        # Sur chaque page, on recupere la liste des adherent qu'on ecrit dans le fichier csv
        while page_courante < nombre_page:
            page_courante += 1
            r = requests.get(helloAsso_url_adhesions+'&page='+str(page_courante), auth=(hello_asso_user, hello_asso_pass)) 
            r_json = r.json()
            adherents = r_json.get("resources")
            for adherent in adherents:
                nombre_adherents +=1
                
                ad_id = adherent.get("id")
                ad_nom = adherent.get("last_name")
                ad_prenom = adherent.get("first_name")
                ad_type_adhesion = adherent.get("option_label")
                
                ad_date_inscription = adherent.get("date")
                
                ad_tel = ""
                ad_adresse = ""
                ad_ville = ""
                ad_code_postal = ""
                ad_date_naissance = ""
                
                for custom_info in adherent.get("custom_infos"):
                    label = custom_info.get("label")
    
                    if label == "Email contributeur":
                        ad_email = custom_info.get("value")                    
                    elif label == "Numéro de téléphone":
                        ad_tel = custom_info.get("value")
                    elif label == "Adresse":
                        ad_adresse = custom_info.get("value")
                    elif label == "Code postal":
                        ad_code_postal = custom_info.get("value")
                    elif label == "Localité":
                        ad_ville = custom_info.get("value")    
                    elif label == "Date de naissance":
                        ad_date_naissance = custom_info.get("value")                      
                
                
                #["id", "Date Adhesion" , "Nom", "Prenom", "email", "detection doublon" ,  "Adhesion", "Telephone", "Adresse", "Ville", "Code Postal"]                           
                
                detection_doublon="=NB.SI(E:E;E"+str(nombre_adherents+1)+")"
                csv_line =  [ad_id, ad_date_inscription, ad_nom, ad_prenom, ad_email,detection_doublon , ad_type_adhesion, ad_tel, ad_adresse, ad_ville, ad_code_postal]       
                # on enleve les fin de ligne qui pourrait se trouver en plein milieu d'une ligne
                csv_line = [word.strip() for word in csv_line]
                csv_writer.writerow(csv_line)
            
            print("page " + str(page_courante) + " sur " + str(nombre_page) + " traite")
            
    print("fin de traitement")
    print("Nombre adhérents : " + str(nombre_adherents))

def parse_params(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--campagne', required=True, help='Id de la campagne helloAsso')  
    parser.add_argument('-u', '--username', required=True, help='Username de API HelloAsso')    
    parser.add_argument('-p', '--password', required=True, help='Password de API HelloAsso') 
    
    return parser.parse_args(argv)
    

def main(argv):
    args = parse_params(argv)
    get_hello_asso_adhesion(args.campagne , args.username, args.password) 

if __name__ == "__main__":
    main(sys.argv[1:])



