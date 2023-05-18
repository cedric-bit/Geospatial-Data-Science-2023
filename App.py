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


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Dashboard"
        self.left = 150
        self.top = 124
        self.width = 1600
        self.height = 720
        self.current_date = "30/03/2023"
        self.path = 'C:\Work\geospatial'
        self.gtfs_files = []
        self.gtfsrt_files = []
        self.gtfs_file_path = ""
        self.stops_df = []
        self.stop_times_df = []
        self.trips_df = []
        self.routes_df = []
        self.trip_updates = []
        self.trip_updates_with_schedule = []

        self.initUI()
        self.load_data()

    def initUI(self):
        """
        Crée l'interface graphique
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.search_bar_label = QLabel(self)
        self.search_bar_label.setText("  Type stop name to \ncheck train stop times")
        self.search_bar_label.move(115, 30)
        self.search_bar_label.resize(150, 50)
        self.search_bar_label.setFont(QFont("Arial", 10))

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

        self.hbox = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.resize(200, 20)
        self.search_bar.move(75, 75)
        self.hbox.addWidget(self.search_bar)
        self.setLayout(self.hbox)
        self.search_bar.returnPressed.connect(lambda: self.check_stop(self.search_bar))

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

        self.show()

    def buttons(self):

        self.real_time = QPushButton("moving trains", self)
        self.real_time.setToolTip('See real movement of trains')
        self.real_time.move(745, 100)
        self.real_time.clicked.connect(lambda: self.display_train())

    def display_train(self):
        # To do : open window with trains moving
        print("Map of trains in brussels")

    def show_delays(self):
        # To do : get data about delays and show it on the left side of the map
        # maybe add total delay of each train line and give top delayed line
        print("Delays")

    def check_stop(self, search_bar):
        # checks if the stop name is in the db, for now it only works with "Gare du Nord" write it as it is
        self.stop = self.search_bar.text()  # gets text from the search bar
        if self.stop in self.stops_df['stop_id'].values[0]:
            self.show_stop(search_bar)
        else:
            self.search_bar_label.setText("This stop does not exist")

    def show_stop(self, search_bar):
        # user types stop name, give times of each train passing in this stop, choose date for this aswell
        self.stop = self.search_bar.text()  # gets text from the search bar
        self.stop_window = QMainWindow(self)
        self.stop_window.setWindowTitle("Stop window")
        self.stop_window.setGeometry(self.left, self.top, self.width, self.height)  # probably change these values
        self.date = QLabel(self.stop_window)
        self.date.setText(self.current_date)
        self.date.move(770, 50)
        self.incr_date = QPushButton(">", self.stop_window)
        self.decr_date = QPushButton("<", self.stop_window)
        self.decr_date.move(650, 50)
        self.incr_date.move(850, 50)
        self.incr_date.clicked.connect(lambda: self.new_date(1))
        self.decr_date.clicked.connect(lambda: self.new_date(-1))

        self.stop_table = QTableWidget(self.stop_window)
        self.stop_table.setColumnCount(3)
        self.stop_table.setHorizontalHeaderLabels(["Line n°", "Scheduled arrival time", "Delay"])
        self.stop_table.setRowCount(10)  # set row count to however many trains passing that day
        self.stop_table.resize(400, 600)
        self.stop_table.move(590, 100)
        self.stop_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)  # Stretch columns to fill the available space

        self.stop_title = QLabel(self.stop_window)
        self.stop_title.resize(300, 40)
        self.stop_title.setText(self.search_bar.text())  # Stop name as title
        self.stop_title.setFont(QFont("Arial", 16))
        self.stop_title.move(740, 20)

        self.stop_window.show()

    def new_date(self, modification):
        # move from day to day, get real data instead of "next date" etc
        if modification == 1:
            self.date.setText("next date")
        else:
            self.date.setText("previous date")

    #    ------------------------------------------ Data handling ------------------------------------------

    def load_data(self):
        self.open_files()
        self.real_time_gtfs()

    def read_gtfs_static_file(self, file_path):
        # print(f"Ouverture du fichier {file_path}")
        with zipfile.ZipFile(file_path, 'r') as z:
            stops_df = pd.read_csv(z.open('stops.txt'))
            stop_times_df = pd.read_csv(z.open('stop_times.txt'))
            trips_df = pd.read_csv(z.open('trips.txt'))
            routes_df = pd.read_csv(z.open('routes.txt'))

        return stops_df, stop_times_df, trips_df, routes_df

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
            self.stops_df, self.stop_times_df, self.trips_df, self.routes_df = self.read_gtfs_static_file(gtfs_file)
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

    def merge_trip_updates_and_schedule(self):
        for update in self.trip_updates:
            trip_id = update['trip_id']
            stop_id = update['stop_id']

            stop_time = self.stop_times_df.loc[
                (self.stop_times_df['trip_id'] == trip_id) & (
                            self.stop_times_df['stop_id'] == stop_id), 'arrival_time'].values
            if len(stop_time) > 0:
                scheduled_arrival_time = stop_time[0]

                self.trip_updates_with_schedule.append({
                    'trip_id': trip_id,
                    'route_id': update['route_id'],
                    'stop_id': stop_id,
                    'scheduled_arrival_time': scheduled_arrival_time,
                    'actual_arrival_time': update['arrival_time'],
                    'delay': update['delay']
                })

    def real_time_gtfs(self):
        feed_realtime = self.process_gtfsrt_file(self.gtfsrt_files[0])
        if feed_realtime is not None:
            self.extract_trip_updates(feed_realtime)
            self.merge_trip_updates_and_schedule()

def main():
    app = QApplication(sys.argv)
    App()
    sys.exit(app.exec_())


main()
