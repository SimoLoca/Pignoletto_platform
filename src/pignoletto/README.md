# Pignoletto-project

### Installazione
* Installare QGIS
```
sudo apt install gnupg software-properties-common
wget -qO - https://qgis.org/downloads/qgis-2021.gpg.key | sudo gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import
sudo chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg
sudo add-apt-repository "deb https://qgis.org/ubuntu-ltr $(lsb_release -c -s) main"
sudo apt update
sudo apt install qgis python-qgis qgis-plugin-grass
```
* Seguire le istruzioni all'interno della cartella 'lizmap-wps-web-client'.
* Dopo aver creato e avviato i container, installare le librerie python necessarie:
```
pip3 install -r requirements.txt
```
* Avviare la piattaforma:
```
python3 run.py
```


### Struttura del progetto pignoletto
* run.py -> script per l'avvio di Flask
* requirements.txt -> file con i pacchetti necessari per avviare l'app
* pignoletto -> package principale
  * QGISManager -> pacchetto in cui all'interno vi sono le classi che gestiscono il progetto QGIS e il file di configurazione di Lizmap
    * QGISManager.py
    * lizmap_API.py
  * _api -> package in cui all'interno andranno implementati quei metodi richiamabili tramite API
    * _api.py
  * _frontend -> package che gestisce la parte di UI dell'applicazione: login, visualizzazione e upload
    * _frontend.py
    * templates
      * *.html
    * static -> file css + eventuali Javascript
  * DBManager.py -> classe che interagisce col DB
  * __init__.py -> inizializza le istanze delle classi che verranno utilizzate, linka i blueprint, espone le risorse (definite in resources.py) sull'API e crea il file qgs e cfg
  * config.json -> contiene parametri di configurazione e variabili sensibili
  * models.py -> tramite ORM sqlalchemy mappa le tabelle presenti nel DB nell'applicazione
  * resources.py -> definisce le "risorse" che potranno essere esposte tramite API
