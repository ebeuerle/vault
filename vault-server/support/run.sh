#!/bin/sh

set -ex

# Check vault version >= 0.9.3
version=$(vault version | awk '{ print $2 }' | sed 's/^v//')
major_version=$(echo "$version" | cut -d. -f1)
minor_version=$(echo "$version" | cut -d. -f2)
patch_version=$(echo "$version" | cut -d. -f3)
if [ "$major_version" -le 0 ] && [ "$minor_version" -le 9 ] && [ "$patch_version" -lt 3 ]; then
  echo "Please run 'docker pull vault' to get an up-to-date version of vault"
  exit 1
fi

# Hey there! We need vault *inside* the container to listen on a different port
# from the default (8200) to avoid a port conflict. You should use 8200 outside
# and basically forget about the fact that 8250 is used here.

export VAULT_ADDR="http://127.0.0.1:8250"

nohup vault server -dev -dev-root-token-id="token-root" \
  -log-level=debug -config=/vault/config/ -dev-listen-address="0.0.0.0:8250" &
VAULT_PID=$!

count=1
while [ "$count" -le 60 ]; do
  if vault status; then break; fi
  count=$((count+1))
  sleep 0.5
done

vault status

# Known secret, for testing
vault write secret/_known kittens=awesome

# Configure LDAP auth
vault auth enable ldap
vault write auth/ldap/config \
  url="ldaps://ldap.example.net" \
  userattr="uid" \
  userdn="ou=people,dc=example,dc=net" \
  discoverdn=true \
  groupdn="ou=groups,dc=example,dc=net" \
  insecure_tls=false \
  starttls=true

# Create stub policies to match the example output
vault write sys/policy/vault-full-administrative-access policy=@/vault/support/policy.json
vault write sys/policy/vault-kubernetes-secrets policy=@/vault/support/policy.json
vault write sys/policy/vault-puppet-secrets policy=@/vault/support/policy.json
vault write sys/policy/vault-new-hire-secrets policy=@/vault/support/policy.json
vault write sys/policy/vault-not-so-secret-secrets policy=@/vault/support/policy.json

# Create the original configuration to match the example output
vault write auth/ldap/groups/cn=security,ou=groups,dc=example,dc=net policies=vault-full-administrative-access
vault write auth/ldap/groups/cn=sre,ou=groups,dc=example,dc=net policies=vault-full-administrative-access,vault-not-so-secret-secrets
vault write auth/ldap/groups/cn=terminated-employees,ou=groups,dc=example,dc=net policies=vault-not-so-secret-secrets

# Log to STDOUT
vault audit enable file file_path=stdout

# Don't exit 'til vault does
wait $VAULT_PID
