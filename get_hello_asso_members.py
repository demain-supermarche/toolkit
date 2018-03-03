# get_hello_asso_members.py
# Python3
# author : Fafadji GNOFAME
# Date : 03 mars 2018
# Version : 1.0
# Description :  get all helloAsso members and write then in a csv file

import requests, csv, sys, argparse


def get_hello_asso_members_url(compaign_id, created_from):
    results_per_page = 100
        
    hello_asso_url_params = "type=SUBSCRIPTION&results_per_page="+str(results_per_page)+"&from="+created_from
    hello_asso_url_members = "https://api.helloasso.com/v3/campaigns/"+compaign_id+"/actions.json?"+hello_asso_url_params
    
    return hello_asso_url_members

def format_member(member, member_number):
    m_id, m_name, m_surname = member.get("id"), member.get("last_name"), member.get("first_name")
    m_subs_type, m_subs_date = member.get("option_label"), member.get("date")
    
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
                               
    duplication = "=NB.SI(E:E;E"+str(member_number+1)+")"
    
    #["id", "Date Adhesion" , "Nom", "Prenom", "email", "detection doublon" ,  "Type Adhesion", "Telephone", "Adresse", "Ville", "Code Postal", "Url carte adherent"]                            
    csv_line =  [m_id, m_subs_date, m_name, m_surname, m_email,duplication , m_subs_type, m_phone, m_address, m_city, m_zip_code, m_card_url]       
    # strip "\n" to prevent undesirable end of line in the csv file
    csv_line = [word.strip() for word in csv_line]
    
    return csv_line
        

def get_hello_asso_members(compaign_id, hello_asso_user, hello_asso_pass, created_from = ""):
    
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
    
    # Opening the csv file
    with open('adherents_hello_asso.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='|', quotechar=' ', quoting=csv.QUOTE_MINIMAL)   
        
        # Writting the header's line in the csv file
        csv_line_header =  ["id", "Date Adhesion" , "Nom", "Prenom", "email", "detection doublon" ,  "Type Adhesion", "Telephone", "Adresse", "Ville", "Code Postal", "Url carte adherent"]       
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
    

def parse_params(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--campaign', required=True, help='Id de la campagne helloAsso') 
    parser.add_argument('-s', '--start_date', required=False, default="", 
        help='Date de debut a partir de laquelle recuperer les adhesions. Si non renseigne, correspond a la date de debut de la campagne. Exemple de date : -s "2017-04-01T00:00:00"')  
    parser.add_argument('-u', '--username', required=True, help='Nom utilisateur de API HelloAsso')    
    parser.add_argument('-p', '--password', required=True, help='Mot de passe de API HelloAsso') 
    
    return parser.parse_args(argv)
    

def main(argv):
    print("[INFO] Debut Traitement")
    
    args = parse_params(argv)
    get_hello_asso_members(args.campaign , args.username, args.password, args.start_date)
    
    print("[INFO] Fin Traitement")

if __name__ == "__main__":
    main(sys.argv[1:])



