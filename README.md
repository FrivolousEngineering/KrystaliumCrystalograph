# KrystaliumCrystalograph
One of the props for the Alchemists for Krystalium.

# How to install

Create a new venv
```
python3 -m venv venv
```

Activate the venv
```
source venv/bin/activate
```

Install all python dependencies
```
python3 -m pip install -r requirements.txt
```


Move the service files to the right spot
```
sudo cp crystalograph.service /lib/systemd/system/
sudo cp sql_app/crystal-database.service /lib/systemd/system/
```

Force systemd to recognise these files
```
sudo systemctl daemon-reload
```

Enable both of them (this will ensure that they auto-boot)
```
sudo systemctl enable crystalograph.service
sudo systemctl enable crystalograph-database.service
```

# Development
The old (and still current) setup requires the database to be running (as the old system only used the identifier of the RFID cards, which it then uses to ask the DB what traits it has). The newer system uses the stored traits on the card to show what it needs.

The database can be started (in a seperate terminal) with
```
uvicorn sql_app.main:app
```

The display can be started with (NOTE: the -w is to ensure that it doesn't show in fullscreen, which makes debugging easier!)
```
python3 game.py -w
```
