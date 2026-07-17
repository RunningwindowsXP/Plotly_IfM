import openpyxl
import pyodbc
import os

# ---------------------------------------------
# Pfade
# ---------------------------------------------
excel_path = input("Pfad zur Excel-Datei: ").strip('"')
access_path = input("Pfad zur Access-Datei (.accdb): ").strip('"')
jahr = input("Auf welches Jahr beziehen sich die Daten?")

if not os.path.exists(excel_path):
    raise FileNotFoundError(excel_path)

if not os.path.exists(access_path):
    raise FileNotFoundError(access_path)

# ---------------------------------------------
# Excel öffnen
# ---------------------------------------------
wb = openpyxl.load_workbook(excel_path, data_only=True)

# ---------------------------------------------
# Access verbinden
# ---------------------------------------------
conn = pyodbc.connect(
    rf"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_path};"
)
cur = conn.cursor()

# Tabelle leeren (optional)
cur.execute("DELETE FROM Wirtschaftszweige")
conn.commit()

id_nr = 0

for ws in wb.worksheets[2:]:

    wirtschaftszweig = ws.title

    bereiche = [
        "H9:L13",      # Anzahl
        "M9:Q13",      # Abhängig Beschäftigte
        "R9:V13",      # SV-Beschäftigte
        "W9:AA13",     # Geringfügig Beschäftigte
        "AB9:AF13"     # Umsatz in 1000€
    ]

    for umsatzklasse, rng in enumerate(bereiche, start=1):

        block = []

        for row in ws[rng]:
            block.append([
                None if c.value == "." else c.value
                for c in row
            ])

        # Jede Zeile des Blocks wird ein Datensatz
        for beschaeftigtenklasse in range(5):

            werte = block[beschaeftigtenklasse]

            cur.execute("""
                INSERT INTO Wirtschaftszweige
                (
                    ID,
                    Jahr,
                    Wirtschaftszweig,
                    Umsatzklasse,
                    Beschäftigtenklasse,
                    Anzahl,
                    [Abhängig Beschäftigte],
                    [SV-Beschäftigte],
                    [Geringfügig Beschäftigte],
                    [Umsatz in 1000€]
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_nr,
                jahr,
                wirtschaftszweig,
                umsatzklasse,
                beschaeftigtenklasse + 1,

                werte[0],
                werte[1],
                werte[2],
                werte[3],
                werte[4],
            ))

            id_nr += 1

conn.commit()
conn.close()

print(f"Fertig! {id_nr} Datensätze importiert.")