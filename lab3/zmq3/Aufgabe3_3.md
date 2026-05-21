# Aufgabe 3.3
>Erklären Sie das Verhalten der Systeme in den beiden Experimenten.

##### tasksrc.py
1. ID (1 oder 2), Adresse und Port festlegen
2. Push-Socket erstellen und mit Adresse damit verbinden
3. Kurz auf Clients warten
4. Serialisierte Daten, ID und "workload" (random 1 - 100), als bytes auf Socket abschicken

##### taskwork.py
1. ID (1 oder 2), 2 Adressen mit je einem Port festlegen (von 2 möglichen sources)
2. Pull-Socket erstellen und mit beiden Adressen damit verbinden
3. Wartet auf Nachrichten, bei Erhalt:
    1. Deserialisieren
    2. Daten ausgeben (eigene ID, workload und source ID)
    3. Arbeit simulieren (kurz time.sleep)


##### Ablauf 1. Experiment
1. Zwei sources mit ID 1 und 2, ein worker
2. Sources schicken auf zwei verschiedenen Ports workloads (über Socket)
3. Worker empfängt Nachrichten auf beiden Ports (über Socket), erkennbar über output von source ID 1 und 2
4. Worker "arbeitet" sequentiell Nachrichten beider sources ab

##### Ablauf 2. Experiment
1. Eine sources, zwei worker mit ID 1 und 2
2. Source schickt auf einem Port workloads (über Socket)
3. Worker 1 und 2 empfangen Nachrichten auf einem Port (über Socket), der andere ist inaktiv
4. Worker "arbeiten" beide gleichzeitig unterschiedliche Nachrichten der source ab


##### Was auffällt:
- Experiment 1 - doppelt so viel Arbeit für einen worker
- Experiment 2 - halb so viel Arbeit für einen worker
- Worker in Experiment 2 arbeiten gleichzeitig und splitten sich die Arbeit