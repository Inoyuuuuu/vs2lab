# Aufgabe 3.1
>Erklären Sie das Verhalten der Systeme in den beiden Experimenten.

##### Client.py
1. Adresse wird festgelegt mit host-adresse auf socket1
2. Request-Socket wird über ZeroMQ Context erzeugt und client verbindet sich zu diesem
3. Client schickt Nachricht und blockiert Socket bis Antwort empfangen wird
4. Entschlüsselt empfangene Antwort, printet diese und fährt mit for-Schleife fort

##### Client1.py
1, 2 gleich wie bei 1 nur bei client und client1
3. Clients schicken beide Nachrichen und blockieren ihren Socket bis Antworten empfangen werden
4. Entschlüsseln empfangene Antworten, printen diese und fahren fort

##### Server
1. Server erstellt 1 Sockets und bindet 2 Adressen mit Port 1 und 2 (einen für client und einen für client2)
2. Wartet auf Nachrichten
3. Bei erhalt (falls nicht "STOP") entschlüsselt sie, formatiert sie mit zusaätzlichem string und schickt diese verschlüsselt wieder zurück
4. Bei erhalt von "STOP" endet das Server-Skript

##### Was auffällt:
- Client hat (bei 3 versuchen) vorrang über client1, auch wenn später gestartet
- Liegt daran, dass server parallel auf beide prozesse warted und nicht sequenziell vorgeht