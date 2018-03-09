# get_odoo_members.py
# Python3
# author : Fafadji GNOFAME
# Date : 03 mars 2018
# Version : 1.0
# Description :  get all odoo members and write then in a csv file

import ssl, pprint, csv, argparse, sys
from xmlrpc import client
from functions import *


def get_odoo_members(odoo_username, odoo_password, url, db, output_file):
    print("[INFO] Debut Traitement")
    print("[INFO] Recuperation de la liste des adherents")
    print("[INFO]    URL odoo : " + url)
    print("[INFO]    Base de donnee odoo : " + db)
    
    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url), context=ssl._create_unverified_context())
    uid = common.authenticate(db, odoo_username, odoo_password, {})
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=ssl._create_unverified_context())
    
    members = models.execute_kw(db, uid, odoo_password, 'res.partner', 'search_read', 
                        [[['is_company', '=', False]]], 
                        {'fields': ['id', 'ref', 'active', 'member_lines', 'write_date', 'name', 'email', 'mobile', 
                                    'phone', 'street', 'street2', 'zip', 'city', 'birthdate']})
    
    members_count = len(members)
    
    if members_count > 0:
        create_path_n_file_if_needed(output_file)
        with open('adherents_odoo.csv', 'w') as csvfile:
    
            dict_keys = members[0].keys()
    
            csv_writer = csv.DictWriter(csvfile, dict_keys, delimiter='|', quotechar=' ', quoting=csv.QUOTE_MINIMAL) 
            csv_writer.writeheader()
            csv_writer.writerows(members)
    
    print("[INFO] Nombre d'adherents: " + str(members_count))
    print("[INFO] Fichier de sortie : " + output_file)
    print("[INFO] Fin Traitement")

def parse_params(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True, help='Nom utilisateur de connexion a odoo')    
    parser.add_argument('-p', '--password', required=True, help='Mot de passe de connexion a odoo') 
    parser.add_argument('-url', '--url', required=True, help='URL odoo') 
    parser.add_argument('-db', '--database', required=True, help='Base de donnee odoo')
    parser.add_argument('-o', '--output_file', required=False, default="csv/adherents_odoo.csv",
                        help="Chemin vers le fichier de sortie")    
    
    return parser.parse_args(argv)    

def main(argv):
    args = parse_params(argv)
    get_odoo_members(args.username, args.password, args.url, args.database, args.output_file) 

if __name__ == "__main__":
    main(sys.argv[1:])