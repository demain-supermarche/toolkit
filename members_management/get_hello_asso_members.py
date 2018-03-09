# get_hello_asso_members.py
# Python3
# author : Fafadji GNOFAME
# Date : 03 mars 2018
# Version : 1.0
# Description :  get all helloAsso members and write then in a csv file

import requests, csv, sys, argparse, configparser, os, errno
from members_keys import MembersKeys
from functions import *


def get_hello_asso_members_url(compaign_id, created_from):
    results_per_page = 100
        
    hello_asso_url_params = "type=SUBSCRIPTION&results_per_page="+str(results_per_page)+"&from="+created_from
    hello_asso_url_members = "https://api.helloasso.com/v3/campaigns/"+compaign_id+"/actions.json?"+hello_asso_url_params
    
    return hello_asso_url_members

def format_member(member, member_number):
    m_id, m_name, m_surname = member.get("id"), member.get("last_name"), member.get("first_name")
    m_subs_type, m_subs_date, m_subs_amout = member.get("option_label"), member.get("date"), str(member.get("amount"))
    
    m_card_id = m_id.strip('0')
    m_card_id = m_card_id[:-1]
    m_card_url = "https://www.helloasso.com/associations/les-amis-de-demain/adhesions/adhesion-a-l-association-les-amis-de-demain/carte-adherent?id="+m_card_id
    
    m_phone, m_address, m_city, m_zip_code, m_birthday, m_email = "", "", "", "", "", ""
    
    for custom_info in member.get("custom_infos"):
        label = custom_info.get("label")

        if label == "Email contributeur": m_email = custom_info.get("value")                               
        elif label == "Numéro de téléphone": m_phone = custom_info.get("value")            
        elif label == "Adresse": m_address = custom_info.get("value")           
        elif label == "Code postal": m_zip_code = custom_info.get("value")          
        elif label == "Localité": m_city = custom_info.get("value") 
        elif label == "Date de naissance": m_birthday = custom_info.get("value")    
    
    #["id", "Date Adhesion" , "Nom", "Prenom", "email", "Type Adhesion", "Montant Adhesion", "Telephone", "Adresse", "Ville", "Code Postal", "Url carte adherent"]                            
    csv_line =  [m_id, m_subs_date, m_name, m_surname, m_email , m_subs_type, m_subs_amout, m_phone, m_address, m_city, m_zip_code, m_card_url]       
    # strip "\n" to prevent undesirable end of line in the csv file
    csv_line = [word.strip() for word in csv_line]
    
    return csv_line
        

def get_hello_asso_members(compaign_id, hello_asso_user, hello_asso_pass, output_file , config, created_from = ""):
    
    print("[INFO] Debut Traitement")    
    print("[INFO] Recuperation de la liste des adherents")
    print("[INFO]    ID de la campagne : "+str(compaign_id))
    
    print_date_debut = "[INFO]    Date debut : " 
    
    if created_from == "":
        print_date_debut +="Debut de la campagne"
    else:
        print_date_debut +=created_from
    
    print(print_date_debut)
    
    hello_asso_members_url = get_hello_asso_members_url(compaign_id, created_from)
    
    # First request to retrieve the number of page on witch we will loop
    r = requests.get(hello_asso_members_url+'&page=1', auth=(hello_asso_user, hello_asso_pass))
    if r.status_code != 200:
        print("[ERROR] Erreur lors de la requete. Code HTTP de la reponse: "+str(r.status_code))
        sys.exit(2)
    
    pages_number = r.json().get("pagination").get("max_page")
    
    current_page = 0
    members_count = 0
    

    create_path_n_file_if_needed(output_file)
    # Opening the csv file
    with open(output_file, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)   
        
        m_keys = MembersKeys(config)
        
        # Writting the header's line in the csv file
        csv_line_header =  [m_keys.id, m_keys.subs_date , m_keys.name, m_keys.surname, m_keys.email ,  m_keys.subs_type, 
                            m_keys.subs_amount, m_keys.phone, m_keys.address, m_keys.city, m_keys.zip, m_keys.subs_card_url]       
        csv_writer.writerow(csv_line_header)    
        
        # loop on the pages returned by helloAsso
        # On every page, retreiving the members list and writing them on the csv file
        while current_page < pages_number:
            current_page += 1
            r = requests.get(hello_asso_members_url+'&page='+str(current_page), auth=(hello_asso_user, hello_asso_pass)) 
            r_json = r.json()
            members = r_json.get("resources")
            for member in members:
                members_count +=1
                csv_line = format_member(member, members_count)
                csv_writer.writerow(csv_line)
            
            print("[INFO] Page " + str(current_page) + " sur " + str(pages_number) + " traitee")
            
    print("[INFO] Nombre d'adherents: " + str(members_count))
    print("[INFO] Fichier de sortie : " + output_file)
    print("[INFO] Fin Traitement")
    
    

def parse_params(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--campaign', required=True, help='Id de la campagne helloAsso') 
    parser.add_argument('-s', '--start_date', required=False, default="", 
        help='Date de debut a partir de laquelle recuperer les adhesions. Si non renseigne, correspond a la date de debut de la campagne. Exemple de date : -s "2017-04-01T00:00:00"')  
    parser.add_argument('-u', '--username', required=True, help='Nom utilisateur de API HelloAsso')    
    parser.add_argument('-p', '--password', required=True, help='Mot de passe de API HelloAsso') 
    parser.add_argument('-mc', '--m_k_config_file', required=False, default="param.conf",
                        help="Chemin vers le fichier de configuration des clef d'identification d'un membre")
    parser.add_argument('-o', '--output_file', required=False, default="csv/adherents_hello_asso.csv",
                        help="Chemin vers le fichier de sortie")     
    
    return parser.parse_args(argv)
    

def main(argv):
    args = parse_params(argv)
    
    m_k_config_file = args.m_k_config_file
    config = configparser.ConfigParser()
    config.read(m_k_config_file)
    
    get_hello_asso_members(args.campaign , args.username, args.password, args.output_file, config, args.start_date)

if __name__ == "__main__":
    main(sys.argv[1:])



