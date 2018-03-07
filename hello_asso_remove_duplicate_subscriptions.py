# hello_asso_remove_duplicate_subscriptions.py
# Python3
# author : Fafadji GNOFAME
# Date : 07 mars 2018
# Version : 1.0
# Description :  
#   Script to delete duplicate entries on the hello_asso members list csv file
#   If there is a duplicate entry, the one kept is the one with the lastest subscription date

#   Algorithm
#   IF name+surmane identical with another line THEN
#      IF email OR full postal address identical THEN **
#         Delete duplicate entry
#
# if some info are absent from last member subscription and present in some previous subscription
# we complete the last subscription with info from previous subscription

# ** Hypothesis :
# When we have the name and surname identical, we assume that 
# if the email or the zip code is also identical, then it is the same person
# Indeed, when those condition are met, it is higthly probable that it is the same person
# Why email OR full postal address ? Because it is also probable that when registering twice
# the subscriber induce an error when filling his or her email or full postal address. 
# It is less probable that an error is done on both information . 
# Note that the error migth be on the line we keep, 
# but we will consider that it is an error in the same way that 
# a subscriber (without duplicate) would make the same kind of error when subscribing

# Plaese note that this is a help script, it is advised to check manually afterward.
# For exemple, if there is a duplicate entry with a slice error on the name 
# (Sophie and Sopie), that won't be detected
# 


import requests, csv, sys, argparse
from operator import itemgetter

def delete_duplicate_entries():
    print("[INFO] Debut Traitement") 
    
    name_param, surname_param, email_param = "Nom", "Prenom", "email"
    address_param, city_param, zip_param = "Adresse", "Ville", " Code  Postal "
    subs_date_param = " Date  Adhesion "
    
    # Reading the csv file to build a member list
    members_list = []
    csv_dic_reader = csv.DictReader(open('adherents_hello_asso_test.csv', 'r'), delimiter='|')
    for member in csv_dic_reader:
        member[name_param], member[surname_param] = member[name_param].upper(), member[surname_param].title()
        member[email_param] = member[email_param].lower()
        member[address_param], member[city_param] = member[address_param].lower(), member[city_param].lower()
        member[zip_param] =  member[zip_param].lower()
        
        members_list.append(member)
    
    if len(members_list) == 0:
        SystemExit
        
    
    members_list_ref, members_list_search = list(members_list), list(members_list)
    members_list_final = []
    
    # Algorithm : 
    # Loop on members_list_ref and then for each member
    # search the member on members_list_search : check if name and surname identical and (email or postal address identical)
    # when found delete member from members_list_search and
    # add the member on a temporary list to check for duplicate
    # Then sort the temporary list and then add the member on members_list_final
    # If duplicate entry cannot be identified clearly, add the member on members_list_final_log
       
    for member_ref in members_list_ref:
        members_list_duplicate = []
        
        m_ref_name, m_ref_surname = member_ref[name_param], member_ref[surname_param]
        m_ref_email = member_ref[email_param]
        m_ref_full_address = member_ref[address_param] + member_ref[city_param] + member_ref[zip_param]
        
        for member_seach in members_list_search:
            
            m_search_name, m_search_surname = member_seach[name_param], member_seach[surname_param]
            m_search_email = member_seach[email_param] 
            m_search_full_address = member_seach[address_param] + member_seach[city_param] + member_seach[zip_param]
            
            test_same_name_surname = (m_ref_name == m_search_name and m_ref_surname == m_search_surname)
            test_same_email_or_address = (m_ref_email == m_search_email or m_ref_full_address == m_search_full_address)
            
            if test_same_name_surname and test_same_email_or_address: 
                members_list_duplicate.append(member_seach)
                
        # Removing found items so that in next iteration it will not be in the search_list to be found again                            
        members_list_search = [x for x in members_list_search if x not in members_list_duplicate]
        
        members_list_duplicate_len = len(members_list_duplicate)
        if members_list_duplicate_len >= 1:
            members_list_duplicate_sorted = sorted(members_list_duplicate, key=itemgetter(subs_date_param), reverse=True)
            
            # if some info are absent from last member subscription and present in some previous subscription
            # we complete the last subscription with info from previous subscription
            member_final = members_list_duplicate_sorted[0].copy()
            for m in members_list_duplicate:
                for k,v in m.items():
                    if k not in member_final or member_final[k] == '':
                        member_final[k] = v            
            
            members_list_final.append(member_final)
            
    dict_keys = members_list[0].keys()
    csv_writer = csv.DictWriter(open('adherents_hello_asso_sans_doublon.csv', 'w'), dict_keys, delimiter='|', quotechar=' ', quoting=csv.QUOTE_MINIMAL) 
    csv_writer.writeheader() 
    csv_writer.writerows(members_list_final)
    print("[INFO] Fin Traitement") 

    


def parse_params(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--campaign', required=True, help='Id de la campagne helloAsso') 
    parser.add_argument('-s', '--start_date', required=False, default="", 
        help='Date de debut a partir de laquelle recuperer les adhesions. Si non renseigne, correspond a la date de debut de la campagne. Exemple de date : -s "2017-04-01T00:00:00"')  
    parser.add_argument('-u', '--username', required=True, help='Nom utilisateur de API HelloAsso')    
    parser.add_argument('-p', '--password', required=True, help='Mot de passe de API HelloAsso') 
    
    return parser.parse_args(argv)
    

def main(argv):
    #args = parse_params(argv)
    delete_duplicate_entries()

if __name__ == "__main__":
    main(sys.argv[1:])



