# acme2cert-exp
Experiments with acme2certifier (https://github.com/grindsa/acme2certifier)

#### Instructions

##### Installation

```
python3 -m pip install virtualenv --user
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run this only once:

```
python3 django_update.py
```

##### Running the development server

```
python3 manage.py runserver
```

Server is configured by [acme_srv.conf](/acme/acme_srv.cfg), domain validation is disabled for now.

##### Testing with certbot (client)

```
certbot certonly --server http://127.0.0.1:8000/ --standalone -d tt.example.com --cert-name tt --agree-tos -m abdo@gmail.com
```


#### What's different from acme2certifier?:

Nearly all code is from acme2certifier repository, with acme implementation with django database store (db_handler)  + django server and scripts, all in one place for the ease of development/experimenting:

List of changes:

* copied django [db_handler.py](https://github.com/grindsa/acme2certifier/blob/master/examples/db_handler/django_handler.py) inside [acme](/acme) as `db_handler`.
* rename the django app module [acme](https://github.com/grindsa/acme2certifier/tree/master/examples/django/acme) to be `app` inn all relevant places to avoid import conflicts with acme implementation module.
* updated [settings.py](/acme2certifier/settings.py) of django app to work with sqlite database instead of mysql.
* generated keys and certificates to run the [openssl ca handler](https://github.com/grindsa/acme2certifier/blob/master/docs/openssl.md) at [acme_ca](/acme_ca) and added the configuration for it at [acme_srv.conf](/acme/acme_srv.cfg#L20).


Work on progress:

* adding a ca handler implementation which gets certs via zerossl rest api.
