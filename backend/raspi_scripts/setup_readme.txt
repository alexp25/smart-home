
sudo nano /etc/systemd/system/wsapp.service

sudo systemctl daemon-reload

sudo systemctl enable wsapp.service



sudo systemctl start wsapp.service

sudo systemctl status wsapp.service


sudo journalctl -u wsapp.service -n 100

