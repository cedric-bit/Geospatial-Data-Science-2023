import os
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# Créer le moteur
engine = create_engine('postgresql://postgres:azerty@localhost:5432/SNCB')

# Fonction pour exécuter l'instruction COPY
def execute_copy_from(cursor, table_name, file_path):
    # Vérifier si le fichier existe
    if not os.path.exists(file_path):
        print(f"Le fichier '{file_path}' n'existe pas.")
        return
    
    # Exécuter COPY FROM en utilisant copy_from()
    with open(file_path, 'r') as f:
        # Ignorer la première ligne si elle contient des en-têtes
        next(f)
        
        cursor.copy_from(f, table_name, sep=',', null='')

# Établir une connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='azerty',
    database='SNCB'
)

# Créer un curseur
cursor = conn.cursor()

# Exécuter l'instruction COPY pour stop_time_overrides.txt
stop_time_overrides_file_path = r'C:\Users\Administrateur\GNS3\stop_time_overrides.txt'
execute_copy_from(cursor, 'stop_time_overrides', stop_time_overrides_file_path)

# Exécuter l'instruction COPY pour stop_times.txt
stop_times_file_path = r'C:\Users\Administrateur\GNS3\stop_times.txt'
execute_copy_from(cursor, 'stop_times', stop_times_file_path)

# Exécuter l'instruction COPY pour stops.txt
stops_file_path = r'C:\Users\Administrateur\GNS3\stops.txt'
execute_copy_from(cursor, 'stops', stops_file_path)

# Exécuter l'instruction COPY pour transfers.txt
transfers_file_path = r'C:\Users\Administrateur\GNS3\transfers.txt'
execute_copy_from(cursor, 'transfers', transfers_file_path)

# Exécuter l'instruction COPY pour translations.txt
translations_file_path = r'C:\Users\Administrateur\GNS3\translations.txt'
execute_copy_from(cursor, 'translations', translations_file_path)

# Exécuter l'instruction COPY pour trips.txt
trips_file_path = r'C:\Users\Administrateur\GNS3\trips.txt'
execute_copy_from(cursor, 'trips', trips_file_path)


# Exécuter l'instruction COPY pour calendar.txt
calendar_file_path = r'C:\Users\Administrateur\GNS3\calendar.txt'
execute_copy_from(cursor, 'calendar', calendar_file_path)

# Exécuter l'instruction COPY pour calendar_dates.txt
calendar_dates_file_path = r'C:\Users\Administrateur\GNS3\calendar_dates.txt'
execute_copy_from(cursor, 'calendar_dates', calendar_dates_file_path)

# Exécuter l'instruction COPY pour routes.txt
routes_file_path = r'C:\Users\Administrateur\GNS3\routes.txt'
execute_copy_from(cursor, 'routes', routes_file_path)
# Valider les modifications
conn.commit()

# Fermer le curseur et la connexion
cursor.close()
conn.close()