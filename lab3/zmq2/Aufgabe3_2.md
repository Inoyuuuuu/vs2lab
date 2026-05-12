# Aufgabe 3.2
>Erklären Sie das Verhalten der Systeme in den beiden Experimenten.

##### Client.py
1. Subscriber-Socket wird über ZeroMQ Context erzeugt
2. Host-Adresse und Port werden festgelegt
3. Client verbindet Subscriber-Socket und Adresse + Port
4. Client setzt Socket-Optionen "TIME" abbonieren
5. Client wartet 5 mal auf Nachrichten auf dem Socket und gibt diese bei erhalt aus

##### Client1.py
1, 2, 3 gleich wie bei Client.py
4. Client setzt Socket-Optionen "DATE" abbonieren
5. Client wartet 3 mal auf Nachrichten auf dem Socket und gibt diese bei erhalt aus

##### Server
1. Publisher-Socket wird über ZeroMQ Context erzeugt
2. Host-Adresse und Port werden festgelegt
3. Client verbindet Publisher-Socket und Adresse + Port
4. Alle 5 Sekunden schickt Server zwei in bytes verpackte Nachrichten mit "TIME" und "DATE" tag mit jeweils der Uhrzeit und dem Datum


##### Was auffällt:
- Clients in beiden Experimenten arbeiten parallel
- Erhalten zur gleichen Zeit Nachrichten vom Server und geben diese auch gleichzeitig aus