#####################
### Massagedevice ###
#####################

# Verion 08 Massagedevice 02.01.2020
#       - Gui umgestalltet
#       - Bugfixes

# Verion 07 Massagedevice
#       - WS IP wird vom Server geliefert
#       - Bugfixes

# Verion 07 Massagedevice
#       - Gui wird auch im Random-Mode aktualisiert
#       - Bugfixes

# Verion 06 Massagedevice
#       - Shell-Script start.sh
#       - Bugfixes

# Verion 05 Massagedevice
# Funktionen: GUI Okay, inkl. Random-Mode
#       - Strat / Stop Device
#       - Level einstellen
#       - Mode einstellen
#       - Random-Mode mit mehreren Iterationen
#       - Random Duration einstellbar
#       - Randem Max / Min Level einstellbar

pi@raspberrypi:~ $ python
Python 3.9.2 (default, Mar 12 2021, 04:06:34)
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>

andreas@massagedevice:~/massagedevice $ sudo pip list
Package       Version
------------- ---------
certifi       2020.6.20
chardet       4.0.0
colorzero     1.1
distro        1.5.0
gpiozero      1.6.2
idna          2.10
numpy         1.19.5
picamera2     0.3.12
pidng         4.0.9
piexif        1.1.3
Pillow        8.1.2
pip           20.3.4
python-apt    2.2.1
python-prctl  1.7
requests      2.25.1
RPi.GPIO      0.7.0
setuptools    52.0.0
simplejpeg    1.6.4
six           1.16.0
spidev        3.5
ssh-import-id 5.10
toml          0.10.1
urllib3       1.26.5
v4l2-python3  0.3.2
websockets    10.1
wheel         0.34.2


root@massagedevice:~# cat /etc/systemd/system/massagedevice.service
[Unit]
Description=Massagedevice-Service

[Service]
Type=oneshot
ExecStart=/home/andreas/massagedevice/service.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target

root@massagedevice:~# systemctl status massagedevice.service
● massagedevice.service - Massagedevice-Service
     Loaded: loaded (/etc/systemd/system/massagedevice.service; enabled; vendor>
     Active: active (exited) since Sat 2025-01-04 07:18:24 CET; 5min ago
    Process: 249 ExecStart=/home/andreas/massagedevice/service.sh (code=exited,>
   Main PID: 249 (code=exited, status=0/SUCCESS)
      Tasks: 2 (limit: 414)
        CPU: 3.957s
     CGroup: /system.slice/massagedevice.service
             └─253 python3 /home/andreas/massagedevice/websocket.py

Jan 04 07:18:22 massagedevice systemd[1]: Starting Massagedevice-Service...
Jan 04 07:18:24 massagedevice systemd[1]: Finished Massagedevice-Service.