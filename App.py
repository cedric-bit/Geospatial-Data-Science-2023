import realtime as realtime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap
import sys
import os
from datetime import datetime
import osmnx as ox
from google.transit import gtfs_realtime_pb2
from google.protobuf import text_format
import pandas as pd
import os
import zipfile
import osmium
import datetime
import matplotlib.pyplot as plt
import folium
import geopandas as gpd
from shapely.geometry import Point
import time


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Dashboard"
        self.left = 150
        self.top = 124
        self.width = 1600
        self.height = 720
        self.path = 'C:\Work\geospatial\\2023-03-30'
        self.base_path = 'C:\Work\geospatial\\'
        self.add_path = ['2023-03-18', '2023-03-19', '2023-03-20', '2023-03-21', '2023-03-22', '2023-03-23',
                        '2023-03-24', '2023-03-25', '2023-03-26', '2023-03-27', '2023-03-28', '2023-03-29',
                         '2023-03-30']
        self.gtfs_files = []
        self.gtfsrt_files = []
        self.gtfs_file_path = ""
        self.stops_df = []
        self.stop_times_df = []
        self.trips_df = []
        self.routes_df = []
        self.trip_updates = []
        self.trip_updates_with_schedule = []
        self.file_number = 12   # fichier gtfs = 30 mars on peut changer pour 0
        self.time = 0
        self.file_time = []
        self.load_data()
        self.file_chosen = self.gtfsrt_files[0]
        self.initUI()

    def initUI(self):
        """
        Crée l'interface graphique
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


        mainMenu = self.menuBar()
        exitMenu = mainMenu.addMenu('Quitter')
        exitButton = QAction('Quitter', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        exitMenu.addAction(exitButton)

        self.stops = QLabel(self)
        self.stops.setPixmap(QPixmap("Train stops.png"))
        self.stops.resize(800, 700)
        self.stops.move(400, 10)

        self.dash_title = QLabel(self)
        self.dash_title.resize(300, 40)
        self.dash_title.setText("Train stops in belgium")
        self.dash_title.setFont(QFont("Arial", 16))
        self.dash_title.move(700, 20)

        self.average_label = QLabel(self)
        self.average_label.setText("Most delayed trains")
        self.average_label.move(1330, 50)
        self.average_label.resize(150, 50)
        self.average_label.setFont(QFont("Arial", 10))

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Line n°", "Average Delay", "Biggest Delay"])
        self.table.setRowCount(5)
        self.table.resize(317, 185)
        self.table.move(1230, 100)

        self.buttons()
        self.change_day()
        self.show_delays()
        self.change_time()

        self.show()

    def buttons(self):

        self.real_time = QPushButton("moving trains", self)
        self.real_time.setToolTip('See real movement of trains')
        self.real_time.move(745, 100)
        self.real_time.clicked.connect(lambda: self.display_train())

    def display_train(self):
        # To do : open window with trains moving
        print("Map of trains in brussels")


    def five_delays(self):
        # faire les delays de + de 5 min
        print("to do")



    def show_delays(self):
        # en gros va falloir faire bcp de fonctions de ce style pour montrer d autres choses style average delay etc
        self.big_delay = QLabel(self)
        big_del, big_del_route = self.biggest_delay()
        big_del //= 60
        string = "Biggest delay of today is " + str(big_del) + " minutes on route : " + str(big_del_route)
        self.big_delay.setText(string)
        self.big_delay.move(10, 300)
        self.big_delay.resize(500, 100)

    def biggest_delay(self):
        biggest = 0
        route = None
        x = ""
        for delay in self.trip_updates:
            if delay['delay'] > biggest:
                biggest = delay['delay']
                x = delay['trip_id']
                route = delay['route_id']

        trip = self.trips_df.loc[self.trips_df['trip_id'] == x]
        trip_route = int(trip['route_id'].iloc[0])
        route = self.routes_df.loc[self.routes_df['route_id'] == trip_route]
        route_name = route['route_long_name']

        return biggest, route_name.iloc[0]

    def change_day(self):
        # user types stop name, give times of each train passing in this stop, choose date for this aswell
        self.date = QLabel(self)
        self.date.setText(self.add_path[self.file_number])
        self.date.move(170, 50)
        self.incr_date = QPushButton(">", self)
        self.decr_date = QPushButton("<", self)
        self.decr_date.move(50, 50)
        self.incr_date.move(250, 50)
        self.incr_date.clicked.connect(lambda: self.new_date(1))
        self.decr_date.clicked.connect(lambda: self.new_date(-1))


    def change_time(self):
        # change le fichier gtfs real time
        self.choose_time = QComboBox(self)
        self.choose_time.move(150, 100)
        for i in range(0, len(self.gtfsrt_files), 20):
            epoch_time = self.gtfsrt_files[i].replace(".gtfsrt", "")
            stringz = "C:\\Work\\geospatial\\" + self.add_path[self.file_number] + "\\"
            epoch_time = epoch_time.replace(stringz, "")
            epoch_time = int(epoch_time)
            epoch_time = time.gmtime(epoch_time)
            file_time = str(epoch_time[3]) + "H" + str(epoch_time[4])
            self.file_time.append([self.gtfsrt_files[i], file_time])
            self.choose_time.addItem(file_time)

        #self.choose_time.activated()


    def changing_time(self):
        for i in range(len(self.file_time)):
            if self.choose_time.currentText() == self.file_time[i][1]:
                self.file_chosen = self.file_time[i][0]
                self.real_time_gtfs()

    def new_date(self, modification):
        # move from day to day, get real data instead of "next date" etc
        if modification == 1:
            if self.file_number == 12:
                self.file_number = 0
            else:
                self.file_number += 1
        else:
            if self.file_number == 0:
                self.file_number = 12
            else:
                self.file_number -= 1

        self.date.setText(self.add_path[self.file_number])
        self.path = self.base_path + self.add_path[self.file_number]
        self.trip_updates = []
        self.open_files()
        self.real_time_gtfs()
        
        # update le delay parce qu'un appel a la fonction ca marche pas jsp pk , ne pas delete

        big_del, big_del_route = self.biggest_delay()
        big_del //= 60
        string = "Biggest delay of today is " + str(big_del) + " minutes on route : " + str(big_del_route)
        self.big_delay.setText(string)
        self.big_delay.move(10, 300)
        self.big_delay.resize(500, 100)

    #    ------------------------------------------ Data handling ------------------------------------------

    def load_data(self):
        self.open_files()
        self.real_time_gtfs_first()

    def read_gtfs_static_file(self, file_path):
        # print(f"Ouverture du fichier {file_path}")
        with zipfile.ZipFile(file_path, 'r') as z:
            self.stops_df = pd.read_csv(z.open('stops.txt'))
            self.stop_times_df = pd.read_csv(z.open('stop_times.txt'))
            self.trips_df = pd.read_csv(z.open('trips.txt'))
            self.routes_df = pd.read_csv(z.open('routes.txt'))

    def open_files(self):
        for subdir, dirs, files in os.walk(self.path):
            for file in files:
                # Vérifiez si le fichier est un fichier GTFS zip
                self.gtfs_file_path = os.path.join(subdir, file)
                if file.endswith('.zip'):
                    self.gtfs_files.append(self.gtfs_file_path)
                elif file.endswith('.gtfsrt'):
                    self.gtfsrt_files.append(self.gtfs_file_path)
        # Utilisez les fonctions pour extraire les informations

        for gtfs_file in self.gtfs_files:
            self.read_gtfs_static_file(gtfs_file)
            # Utilisez les DataFrames pour effectuer vos analyses et traitements

    def extract_trip_updates(self, feed_realtime):
        for entity in feed_realtime.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                trip_id = trip_update.trip.trip_id
                route_id = trip_update.trip.route_id
                for stop_time_update in trip_update.stop_time_update:
                    stop_id = stop_time_update.stop_id
                    arrival_time = stop_time_update.arrival.time
                    departure_time = stop_time_update.departure.time
                    delay = stop_time_update.arrival.delay
                    self.trip_updates.append({
                        'trip_id': trip_id,
                        'route_id': route_id,
                        'stop_id': stop_id,
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'delay': delay
                    })

    def process_gtfsrt_file(self, file_path):
        feed = gtfs_realtime_pb2.FeedMessage()

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                feed.ParseFromString(content)
        except Exception as e:
            # print(f"Erreur lors du traitement du fichier {file_path}: {e}")
            return None

        return feed

    def real_time_gtfs(self):
        feed_realtime = self.process_gtfsrt_file(self.file_chosen)
        epoch_time = self.file_chosen.replace(".gtfsrt", "")
        stringz = "C:\\Work\\geospatial\\" + self.add_path[self.file_number] + "\\"
        epoch_time = epoch_time.replace(stringz, "")
        epoch_time = int(epoch_time)
        self.time = time.gmtime(epoch_time)
        if feed_realtime is not None:
            self.extract_trip_updates(feed_realtime)
            # self.merge_trip_updates_and_schedule()

    def real_time_gtfs_first(self):
        feed_realtime = self.process_gtfsrt_file(self.gtfsrt_files[0])
        epoch_time = self.gtfsrt_files[0].replace(".gtfsrt", "")
        stringz = "C:\\Work\\geospatial\\" + self.add_path[self.file_number] + "\\"
        epoch_time = epoch_time.replace(stringz, "")
        epoch_time = int(epoch_time)
        self.time = time.gmtime(epoch_time)
        if feed_realtime is not None:
            self.extract_trip_updates(feed_realtime)
            # self.merge_trip_updates_and_schedule()

def main():
    app = QApplication(sys.argv)
    App()
    sys.exit(app.exec_())


main()
