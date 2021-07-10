import os
import logging
import requests
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
                    new_src[src['dn']] = {'policies':src['policies'], 'filepath': paths + src['dn']}
        #print("Dictionary new_src: {}".format(new_src))

        ###Add group(s)###
        for key in new_src.keys():
            if not key in grp_pols:
                print("Adding: {}".format(new_src[key]['filepath']))
                self.add_group(key,new_src,flag)

        #determine which groups are unchanged in vault or need to be modified
        for k, v in new_src.items():
            for m, n in grp_pols.items():
                if k == m:
                    if v['policies']==n:
                        print("Unchanged: {}{}".format(paths,k))
                        break
                    else:
                        print("K: {}, V: {}, N: {}".format(k,v['policies'],n))
                        #self.mod_group(k,new_src,grp_pols,flag)
                        break

        ###Delete group(s)###
        for key in grp_pols.keys():
            if not key in new_src:
                self.del_group(paths,key,flag)
        
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

    def add_group(self,key,new_src,flag):
        if flag == 'no-op':
            print(" + {}".format(*new_src[key]['policies']))
            return None
        print(" + {}".format(*new_src[key]['policies']))
        url = self.base_url + '/v1/auth/ldap/groups/' + key 
        payload = { 'policies': new_src[key]['policies'][0] }
        #print("Url: {}, Payload: {}".format(url,payload))
        req = requests.post(url,headers=self.headers,verify=self.config.ca_path, json=payload)

        if req.status_code == 200 or req.status_code == 204:
            pass
        else:
            print("Something went wrong")

    def mod_group(self,key,new_src,grp_pols,flag):
        if flag == 'no-op':
            print("Modifying: {}".format(new_src[key]['filepath']))
            return None
        #url = self.base_url + '/v1/auth/ldap/groups/' + grp_name
        #payload = { 'policies': pol }
        #req = requests.post(url,headers=self.headers,verify=self.config.ca_path, payload=payload)
        
        #if req.status_code == 200 or req.status_code == 204:
        #    pass
        #else:
        #    print("Something went wrong")

    def del_group(self,paths,key,flag):
        if flag == 'no-op':
            print("Deleting:  {}{}".format(paths,key))
            return None
        print("Deleting:  {}{}".format(paths,key))
        url = self.base_url + '/v1/auth/ldap/groups/' + key 
        req = requests.delete(url,headers=self.headers,verify=self.config.ca_path)

        if req.status_code == 200 or req.status_code == 204:
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
        #print("Vault groups: {}\n".format(vault_groups))
        for i in vault_groups:
            policies=self.get_policies(i)
            #print("Policy: {} for Vault group: {}".format(policies,i))
            grp_pols[i] = policies
        
        #print("\nGroups and their policies: {}\n".format(grp_pols))
        self.sync_files_to_vault(grp_pols,flag)

def main():
    deploy = DeployPolicyVault()
    deploy.run()

if __name__ == "__main__":
    main()
