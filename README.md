## Prometheus Exporter
Exports json metrics in prometheus

### Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
``` 

### Run:
```
source venv/bin/activate
python3 app.py --port <port> --host <host-url> 
    --basic_auth_user --basic_auth_pass
```
