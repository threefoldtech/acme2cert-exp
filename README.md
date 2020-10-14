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

##### Testing with certbot (client)

```
certbot certonly --server http://127.0.0.1:8000/ --standalone -d tt.example.com --cert-name tt --agree-tos -m abdo@gmail.com
```
