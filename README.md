# cmonitorcli
codiusmonitor.com client executable.

dev requirements:
python => 3.6

Don't forget to update version.py on cli updates.

Establishing connection with the user-interface through the Django channels websockets.

Logic:

Sending codius server status and codiusd usage statistics every 3 seconds.
Responds to the limited amount of commands set in: `services/monitor_service.py` -> `def _execute_command(self, msg)`