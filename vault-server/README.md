# vault-server

This is a simple vault server that you can run with Docker to test your code.

## How-to

### Install docker and docker-compose

- [Install docker](https://docs.docker.com/install/)
- [Install docker-compose](https://docs.docker.com/compose/install/)

### Start the Vault server

Now, from the base checkout of this repository:

```
docker-compose -f vault-server/docker-compose.yml up
```

It will print a bunch of stuff on the screen that will ultimately end with something like:

```
vault-server_1  | 2018/02/08 17:42:43.465882 [DEBUG] audit: adding reload function: path=file/
vault-server_1  | 2018/02/08 17:42:43.465916 [DEBUG] audit: file backend options: path=file/ file_path=stdout
vault-server_1  | 2018/02/08 17:42:43.466930 [INFO ] core: enabled audit backend: path=file/ type=file
vault-server_1  | {"time":"2018-02-08T17:42:43.467500867Z","type":"response","...}
vault-server_1  | Success! Enabled the file audit device at: file/
```

You can make sure it works using:

```
curl -k --header "X-Vault-Token: token-root" https://localhost:8200/v1/secret/_known
{"request_id":"191ac5d7-b568-7a81-090e-d15b5c0be04e","lease_id":"","renewable":false,"lease_duration":2764800,"data":{"kittens":"awesome"},"wrap_info":null,"warnings":null,"auth":null}
```

The vault audit log will print to STDOUT in the window where you started the server.

### Stop the server

Just hit CTRL+C in the window where you ran `docker-compose ... up` above to shut it down.

### Reset the data

We don't have this container set to store any state between runs. Therefore, each time you start the server, it'll be re-initialized from scratch. No need to worry about backups today! :smile_cat:
