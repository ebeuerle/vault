import os
import logging
import requests
import hvac
import yaml
import argparse
import lib

#capture missing SAN warning from vault connection and remove from console
logging.captureWarnings(True)

class DeployPolicyVault():
    def __init__(self):
        self.config = lib.ConfigHelper()
        self.base_url = self.config.protocol + "://" + self.config.url + ":" + self.config.port
        self.token = os.environ['VAULT_TOKEN']
        self.headers = {'X-Vault-Token': self.token}

    def sync_files_to_vault(self,grp_pols,flag):
        src = {}
        new_src = {}
        path = 'auth/ldap/groups'
        paths = 'auth/ldap/groups/'
        for file in os.listdir(path):
            if file.endswith(".yaml"):
                file_path = f"{path}/{file}"
                with open (file_path,'r') as f:
                    src = yaml.load(f)
                    if src['dn'] in grp_pols:
                        new_src[src['dn']] = src['policies']
                    else:
                        print("Adding:   {}{}".format(paths,src['dn']))
                        self.add_group(src['dn'],src['policies'],flag)

        for k, v in new_src.items():
            for m, n in grp_pols.items():
                if m not in new_src:
                    self.del_group(paths,m,flag)
                if v==n:
                    print("Unchanged: {}{}".format(paths,k))
                    break
                else:
                    self.mod_group(paths,k,v,flag)
        #print(new_src)
        #print(grp_pols)

    def get_groups_from_vault(self):
        url = self.base_url + '/v1/auth/ldap/groups?list=true'
        req = requests.get(url,headers=self.headers,verify=self.config.ca_path)
        req_json = req.json()
        groups = req_json['data']['keys']
        
        return groups

    def get_policies(self,group):
        url = self.base_url + '/v1/auth/ldap/groups/' + group
        req = requests.get(url,headers=self.headers,verify=self.config.ca_path)
        req_json = req.json()
        policies = req_json['data']['policies']
        
        return policies

    def add_group(self,grp_name,pol,flag):
        if flag == 'no-op':
            print("  + {}".format(*pol))
            return None
        url = self.base_url + '/v1/auth/ldap/groups/' + grp_name
        payload = { 'policies': pol }
        req = requests.post(url,headers=self.headers,verify=self.config.ca_path, payload=payload)
        if req.status_code == '200':
            pass
        else:
            print("Something went wrong")

    def mod_group(self,paths,grp_name,pol,flag):
        if flag == 'no-op':
            print("Modifying: {}{}".format(paths,grp_name))
            return None
        url = self.base_url + '/v1/auth/ldap/groups/' + grp_name
        payload = { 'policies': pol }
        req = requests.post(url,headers=self.headers,verify=self.config.ca_path, payload=payload)
        if req.status_code == '200':
            pass
        else:
            print("Something went wrong")

    def del_group(self,paths,grp_name,flag):
        if flag == 'no-op':
            print("Deleting:  {}{}".format(paths,grp_name))
            return None
        url = self.base_url + '/v1/auth/ldap/groups/' + grp_name
        req = requests.delete(url,headers=self.headers,verify=self.config.ca_path)
        if req.status_code == '200':
            pass
        else:
            print("Something went wrong")

    def run(self):
        parser = argparse.ArgumentParser(description='Sync static yaml policies to Hashicorp Vault')
        parser.add_argument("--no-op", action="store_true", help="This will allow you to dry-run the sync")
        args = parser.parse_args()
        if args.no_op:
            flag = "no-op"
        else:
            flag = "run"
        grp_pols = {}
        vault_groups = self.get_groups_from_vault()
        for i in vault_groups:
            policies=self.get_policies(i)
            grp_pols[i] = policies
        self.sync_files_to_vault(grp_pols,flag)

def main():
    deploy = DeployPolicyVault()
    deploy.run()

if __name__ == "__main__":
    main()
