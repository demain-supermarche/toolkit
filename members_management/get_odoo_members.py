# get_odoo_members.py
# Python3
# author : Fafadji GNOFAME
# Date : 03 mars 2018
# Version : 1.0
# Description :  get all odoo members and write then in a csv file

import ssl, pprint, csv, argparse, sys
from xmlrpc import client
from functions import *

def set_subs_type_m_not_h_a(member):
    m_subs_type = "Adhesion libre" 
    
    m_comment = str(member['comment'])
    index_subs = m_comment.find("Adhésion")
    if index_subs != -1 :
        sub_tmp = m_comment[index_subs:]
        sub_tmp_split = sub_tmp.split()
        if(len(sub_tmp_split) >= 2):
            m_subs_type = sub_tmp_split[0] + " " + sub_tmp_split[1]
    
    member['membership_type'] = m_subs_type.strip()
       

def set_subs_amount_m_not_h_a(member):
    m_subs_amount = 0
   
    m_comment = str(member['comment'])
    index_subs = m_comment.find("Euro")
    if index_subs != -1 :
        sub_tmp = m_comment[:index_subs]
        sub_tmp_split = sub_tmp.split()
        sub_tmp_split_len = len(sub_tmp_split)
        if(sub_tmp_split_len > 0):
            m_subs_amount = sub_tmp_split[sub_tmp_split_len - 1]
    
    member['membership_amount'] = m_subs_amount

def set_name_surname_m_not_h_a(member):
    name = member['name']
    r_name, surname = "", ""
    
    for word in name.split():
        if word.isupper(): r_name = r_name + word + " " 
        else: surname  = surname + word + " " 
        
    member['r_name'], member['surname'] = r_name.strip(), surname.strip()

def set_subs_date_m_not_h_a(member):
    member['membership_date'] = ""
    
    m_comment = str(member['comment'])
    if "/" in m_comment:
        member['membership_date'] = m_comment.split()[0][:-1]
        

def set_subs_payment_type_m_not_h_a(member):
    m_payment_type = "espece"
    type_cheque = "cheque"
    m_comment = str(member['comment'])        
    index_cheque = m_comment.find(type_cheque)
    
    member['membership_cheque_number']  = ""
    member['membership_cheque_bank_name'] = ""
    
    if index_cheque != -1 :
        m_payment_type = type_cheque
        
        sub_tmp = m_comment[index_cheque:]
        sub_tmp_split = sub_tmp.split()
        sub_tmp_split_len = len(sub_tmp_split)
        if(sub_tmp_split_len >=3):
            check_number = sub_tmp_split[2]
            check_number = check_number[:-1]
            member['membership_cheque_number'] = check_number
        
        
        index_aupres_de = m_comment.find("aupres de")
        aupres_de_len = len("aupres de")
        member['membership_cheque_bank_name'] = m_comment[index_aupres_de+aupres_de_len+1:].strip()
    
    member['membership_payment_type'] = m_payment_type

def get_odoo_members(odoo_username, odoo_password, url, db, output_file):
    print("[INFO] Debut Traitement")
    print("[INFO] Recuperation de la liste des adherents")
    print("[INFO]    URL odoo : " + url)
    print("[INFO]    Base de donnee odoo : " + db)
    
    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url), context=ssl._create_unverified_context())
    uid = common.authenticate(db, odoo_username, odoo_password, {})
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=ssl._create_unverified_context())
    
    fields = ['id', 'ref', 'active', 'member_lines', 'write_date', 'name', 'email', 'mobile', 
                                     'street', 'street2', 'zip', 'city', 'birthdate', 'comment']
    
    members = models.execute_kw(db, uid, odoo_password, 'res.partner', 'search_read', 
                        [[['is_company', '=', False]]], 
                        {'fields': fields})    
    
    members_count = len(members)
    members_h_a_count, members_admin_count = 0, 0
    members_not_h_a, members_admin = [], []
    
    if members_count > 0:
        for member in members:
            for field in [x for x in fields if x not in ['id', 'active']]:
                if str(member[field]) == "False": member[field] = ""
                
            member["comment"] = (str(member["comment"]).strip()).replace('\n','. ')
            m_comment = str(member["comment"])
            str_h_a = "https://www.helloasso.com/associations/les-amis-de-demain/adhesions"
            if str_h_a not in m_comment:
                # membre hors helloAsso
                if "P" in str(member["ref"]):
                    member_copy = member.copy()
                    set_subs_type_m_not_h_a(member_copy)                    
                    set_subs_amount_m_not_h_a(member_copy)
                    set_subs_payment_type_m_not_h_a(member_copy)
                    set_subs_date_m_not_h_a(member_copy)
                    set_name_surname_m_not_h_a(member_copy)
                    
                    members_not_h_a.append(member_copy)
                else: members_admin.append(member)
                    
        
        members_not_h_a_count, members_admin_count = len(members_not_h_a), len(members_admin)
        members_h_a_count = members_count - members_not_h_a_count - members_admin_count
        
        create_path_n_file_if_needed(output_file)
        dict_keys = members[0].keys()
        csv_writer = csv.DictWriter(open(output_file, 'w'), dict_keys, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
        csv_writer.writeheader()
        csv_writer.writerows(members)
        
        output_file_m_not_h_a = "csv/adherents_odoo_hors_h_a.csv"
        create_path_n_file_if_needed(output_file_m_not_h_a)
        dict_keys = members_not_h_a[0].keys()
        csv_writer = csv.DictWriter(open(output_file_m_not_h_a, 'w'), dict_keys, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
        csv_writer.writeheader()
        csv_writer.writerows(members_not_h_a) 
        
        output_file_m_admin = "csv/adherents_odoo_admin.csv"
        create_path_n_file_if_needed(output_file_m_admin)
        dict_keys = members_admin[0].keys()
        csv_writer = csv.DictWriter(open(output_file_m_admin, 'w'), dict_keys, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
        csv_writer.writeheader()
        csv_writer.writerows(members_admin)           
    
    print("[INFO] Nombre d'adherents total : " + str(members_count))
    print("[INFO] Nombre d'adherents helloAsso : " + str(members_h_a_count))
    print("[INFO] Nombre d'adherents hors helloAsso : " + str(members_not_h_a_count))
    print("[INFO] Nombre d'adherents Admin : " + str(members_admin_count))
    print("[INFO] Fichier de sortie tout adherent: " + output_file)
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