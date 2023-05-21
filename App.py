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
        self.width = 1800
        self.height = 900
        self.path = 'C:\Work\geospatial\\2023-03-18'
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
        self.file_number = 0
        self.time = 0
        self.file_time = []
        self.stop_id = 0
        self.routes = []
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
        self.stops.setPixmap(QPixmap("trains.png"))
        self.stops.resize(1400, 900)
        self.stops.move(820, 10)

        self.dash_title = QLabel(self)
        self.dash_title.resize(300, 40)
        self.dash_title.setText("Train stops in belgium")
        self.dash_title.setFont(QFont("Arial", 16))
        self.dash_title.move(1120, 20)

        self.big_delay = QLabel(self)
        self.number_delays = QLabel(self)
        self.number_delays_percentage = QLabel(self)
        self.five_min = QLabel(self)
        self.five_min_percentage = QLabel(self)
        self.five_min_percentage_delays = QLabel(self)

        self.line_big_delay = QLabel(self)
        self.line_number_delays = QLabel(self)
        self.line_five_delays = QLabel(self)
        self.line_number_delays_percent = QLabel(self)
        self.line_five_delays_percent = QLabel(self)
        self.line_five_delays_percent_delays = QLabel(self)


        # ---------------- stop window -------------

        self.search_bar_label = QLabel(self)
        self.search_bar_label.setText("  Type stop name to \ncheck stop information")
        self.search_bar_label.move(335, 450)
        self.search_bar_label.resize(150, 50)
        self.search_bar_label.setFont(QFont("Arial", 10))

        self.hbox = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.resize(200, 20)
        self.search_bar.move(300, 500)
        self.hbox.addWidget(self.search_bar)
        self.setLayout(self.hbox)
        self.search_bar.returnPressed.connect(lambda: self.check_stop(self.search_bar))

        # -----------------------------------------------------------------------------

        self.buttons()
        self.change_time_day()
        self.change_day()
        self.show_delays()
        self.show_number_delays()
        self.show_five_min_delays()
        self.show_line()

        self.show()

    def buttons(self):
        self.choose_time = QComboBox(self)
        self.choose_time.move(350, 100)

        self.update_box = QPushButton("Update time", self)
        self.update_box.move(350, 150)
        self.update_box.clicked.connect(lambda: self.changing_time())

        self.show_lines = QComboBox(self)
        self.update_line = QPushButton("Choose line", self)
        self.show_lines.move(275, 600)
        self.show_lines.resize(250, 30)
        self.update_line.move(350, 650)
        self.update_line.clicked.connect(lambda: self.change_line())

    def show_number_delays(self):
        number = 0
        for delay in self.trip_updates:
            if delay['delay'] > 0:
                number += 1
        if number != 0:
            percentage = number/len(self.trip_updates)
            percentage *= 100
            self.number_delays.setText("The number of delayed trains is : " + str(number) + " out of " + str(len(self.trip_updates)) + " trains")
            self.number_delays_percentage.setText("( " + str(int(percentage)) + "% ) ")
        else:
            self.number_delays.setText("There are no delayed trains at this time")
            self.number_delays_percentage.setText("")

        self.number_delays.move(220, 250)
        self.number_delays.resize(300, 100)
        self.number_delays_percentage.move(500, 250)
        self.number_delays_percentage.resize(100, 100)

    def show_five_min_delays(self):
        number = 0
        total = 0
        for delay in self.trip_updates:
            if delay['delay'] >= 300:
                number += 1
                total += 1
            elif delay['delay'] > 0:
                total += 1
        if number != 0:
            percentage = number/len(self.trip_updates)
            percentage *= 100
            percentage_delays = number/total
            percentage_delays *= 100
            self.five_min.setText("\n" + str(number) + " trains are delayed by more than 5 minutes")
            self.five_min_percentage.setText(" of total \n ( " + str(int(percentage)) + "% ) ")
            self.five_min_percentage_delays.setText("of delayed \n ( " + str(int(percentage_delays)) + "% ) ")
        else:
            self.five_min.setText("There are no delays bigger than 5 minutes at this time")
            self.five_min_percentage.setText("")
            self.five_min_percentage_delays.setText("")


        self.five_min.move(220, 290)
        self.five_min.resize(300, 100)
        self.five_min_percentage.move(510, 290)
        self.five_min_percentage.resize(100, 100)
        self.five_min_percentage_delays.move(450, 290)
        self.five_min_percentage_delays.resize(100, 100)

    def show_delays(self):
        big_del, big_del_route = self.biggest_delay()
        if big_del != 0:
            big_del //= 60
            string = "Biggest delay right now is " + str(big_del) + " minutes on route : " + str(big_del_route)
        else:
            string = "There are no delayed trains at this time"

        self.big_delay.setText(string)
        self.big_delay.move(220, 200)
        self.big_delay.resize(500, 100)

    def biggest_delay(self):
        biggest = 0
        x = ""
        for delay in self.trip_updates:
            if delay['delay'] > biggest:
                biggest = delay['delay']
                x = delay['trip_id']
        if x != "":
            trip = self.trips_df.loc[self.trips_df['trip_id'] == x]
            trip_route = int(trip['route_id'].iloc[0])
            route = self.routes_df.loc[self.routes_df['route_id'] == trip_route]
            route_name = route['route_long_name']

            return biggest, route_name.iloc[0]
        else:
            return biggest, x

    def changing_time(self):
        self.file_chosen = self.file_time[self.choose_time.currentIndex()][0]
        self.real_time_gtfs()
        self.show_delays()
        self.show_number_delays()
        self.show_five_min_delays()

    def change_time_day(self):
        self.choose_time.clear()
        self.file_time = []
        for i in range(0, len(self.gtfsrt_files), 20):
            epoch_time = self.gtfsrt_files[i].replace(".gtfsrt", "")
            stringz = "C:\\Work\\geospatial\\" + self.add_path[self.file_number] + "\\"
            epoch_time = epoch_time.replace(stringz, "")
            epoch_time = int(epoch_time)
            epoch_time = time.gmtime(epoch_time)
            file_time = str(epoch_time[3]) + "H" + str(epoch_time[4])
            self.file_time.append([self.gtfsrt_files[i], file_time])
            self.choose_time.addItem(file_time)

    def change_day(self):
        # user types stop name, give times of each train passing in this stop, choose date for this aswell
        self.date = QLabel(self)
        self.date.setText(self.add_path[self.file_number])
        self.date.move(370, 50)
        self.incr_date = QPushButton(">", self)
        self.decr_date = QPushButton("<", self)
        self.decr_date.move(250, 50)
        self.incr_date.move(450, 50)
        self.incr_date.clicked.connect(lambda: self.new_date(1))
        self.decr_date.clicked.connect(lambda: self.new_date(-1))

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
        self.gtfs_files = []
        self.gtfsrt_files = []
        self.open_files()
        self.change_time_day()
        self.changing_time()
        self.show_delays()
        self.show_number_delays()
        self.show_five_min_delays()
        self.change_line()

    def show_line(self):
        trips = []
        for trip in self.trip_updates:
            if trip['trip_id'] not in trips:
                trips.append(trip['trip_id'])
        for i in range(len(trips)):
            trip = self.trips_df.loc[self.trips_df['trip_id'] == trips[i]]
            trip_route = int(trip['route_id'].iloc[0])
            route = self.routes_df.loc[self.routes_df['route_id'] == trip_route]
            route_name = route['route_long_name']
            self.show_lines.addItem(route_name.iloc[0])

    def change_line(self):
        text = self.show_lines.currentText()
        route = self.routes_df.loc[self.routes_df['route_long_name'] == text]
        trips = []
        route = int(route[('route_id')].iloc[0])
        for i in range(len(self.trips_df)):
            if route == int(self.trips_df['route_id'].iloc[i]):
                trips.append(self.trips_df.iloc[i])

        indexes = []
        for i in range(len(trips)):
            for j in range(len(self.trip_updates)):
                if trips[i]['trip_id'] == self.trip_updates[j]['trip_id']:
                    indexes.append(self.trip_updates[j])

        self.show_line_delays(indexes)
        self.show_big_line_delay(indexes)
        self.show_five_line_delay(indexes)

    def show_line_delays(self, indexes):
        number = 0
        total = 0
        for delay in indexes:
            if delay['delay'] > 0:
                number += 1
        if number != 0:
            percentage = number/len(indexes)
            percentage *= 100
            self.line_number_delays.setText("The number of delayed trains is : " + str(number) + " out of " + str(len(indexes)) + " trains")
            self.line_number_delays_percent.setText("( " + str(int(percentage)) + "% ) ")
        else:
            self.line_number_delays.setText("There are no delayed trains at this time")
            self.line_number_delays_percent.setText("")

        self.line_number_delays.move(220, 750)
        self.line_number_delays.resize(300, 100)
        self.line_number_delays_percent.move(500, 750)
        self.line_number_delays_percent.resize(100, 100)

    def show_big_line_delay(self, indexes):
        big = 0
        for delay in indexes:
            if delay['delay'] > big:
                big = delay['delay']
        if big > 0:
            big = big//60
            self.line_big_delay.setText("The biggest delay right now is : " + str(big) + " minutes")
        else:
            self.line_big_delay.setText("There are no delayed trains at this time")

        self.line_big_delay.move(220, 700)
        self.line_big_delay.resize(300, 100)

    def show_five_line_delay(self, indexes):
        number = 0
        total = 1
        total_n = 0
        for delay in indexes:
            if delay['delay'] > 300:
                number += 1
                total += 1
            elif delay['delay'] > 0:
                total += 1
            total_n += 1

        if number != 0:
            percentage = number/total_n
            percentage *= 100
            percentage_delays = number/total
            percentage_delays *= 100
            self.line_five_delays.setText("The number of delayed trains is : " + str(number) + " out of " + str(total) + " trains")
            self.line_five_delays_percent.setText(" of total \n ( " + str(int(percentage)) + "% ) ")
            self.line_five_delays_percent_delays.setText("of delayed \n ( " + str(int(percentage_delays)) + "% ) ")
        else:
            self.line_five_delays.setText("There are no delays over 5 minutes at this time")
            self.line_five_delays_percent.setText("")
            self.line_five_delays_percent_delays.setText("")

        self.line_five_delays.move(220, 800)
        self.line_five_delays.resize(300, 100)
        self.line_five_delays_percent.move(500, 800)
        self.line_five_delays_percent.resize(100, 100)
        self.line_five_delays_percent_delays.move(700, 800)
        self.line_five_delays_percent_delays.resize(100, 100)

    #    ------------------------------------------- Stop window -------------------------------------------

    def check_stop(self, search_bar):
        self.stop = self.search_bar.text()
        fix = False
        self.search_bar_label.setText("Type stop name to check stop information")
        for name in self.stops_df['stop_name']:
            if not fix:
                if str(name) == self.stop:
                    self.show_stop(search_bar)
                    fix = True
                else:
                    self.search_bar_label.setText("This stop does not exist")
        

    def load_stop_data(self,stop_name):
        stop_data = self.stops_df.loc[self.stops_df['stop_name'] == stop_name]
        stops_id = stop_data.loc[:, 'stop_id']
        self.stop_id = stops_id.iloc[-1]
        self.stop_id = int(self.stop_id)
        list_stopages = []
        bruh = self.stop_times_df['stop_id']
        for i in range(len(self.stop_times_df)):
            if bruh[i] == self.stop_id:
                list_stopages.append(self.stop_times_df.iloc[i])

        return list_stopages


    def show_stop(self, search_bar):
        # user types stop name, give times of each train passing in this stop, choose date for this aswell
        self.stop = self.search_bar.text()  # gets text from the search bar
        self.stop_window = QMainWindow(self)
        self.stop_window.setWindowTitle("Stop window")
        self.stop_window.setGeometry(self.left, self.top, self.width, self.height)  # probably change these values

        self.stop_title = QLabel(self.stop_window)
        self.stop_title.resize(300, 40)
        self.stop_title.setText(self.search_bar.text())  # Stop name as title
        self.stop_title.setFont(QFont("Arial", 16))
        self.stop_title.move(740, 20)

        self.stop_n_delays = QLabel(self.stop_window)
        self.stop_n_delays_percentage = QLabel(self.stop_window)
        self.biggest_delay_stop = QLabel(self.stop_window)
        self.stop_five_delays = QLabel(self.stop_window)
        self.stop_five_delays_percentage = QLabel(self.stop_window)
        self.stop_five_delays_percentage_delays = QLabel(self.stop_window)

        stopages = self.load_stop_data(self.search_bar.text())
        self.show_stop_number_delays()
        self.show_biggest_delay()
        self.show_five_stop_delays()

        self.stop_window.show()


    def show_stop_number_delays(self):
        number = 0
        total = 0
        for delay in self.trip_updates:
            if delay['stop_id'] == str(self.stop_id) and delay['delay'] > 0:
                number += 1
                total += 1
            elif delay['stop_id'] == str(self.stop_id):
                total += 1
        if number != 0:
            percentage = number/total
            percentage *= 100
            self.stop_n_delays.setText("The number of delayed trains is : " + str(number) + " out of " + str(total) + " trains")
            self.stop_n_delays_percentage.setText("( " + str(int(percentage)) + "% ) ")
        else:
            self.stop_n_delays.setText("There are no delayed trains at this time")
            self.stop_n_delays_percentage.setText("( 0% ) ")

        self.stop_n_delays.move(220, 250)
        self.stop_n_delays.resize(300, 100)
        self.stop_n_delays_percentage.move(500, 250)
        self.stop_n_delays_percentage.resize(100, 100)

    def show_biggest_delay(self):
        biggest = 0
        total = ''
        for delay in self.trip_updates:
            if delay['stop_id'] == str(self.stop_id) and delay['delay'] > biggest:
                biggest += delay['delay']
                total = delay['trip_id']
        if total != '':
            trip = self.trips_df.loc[self.trips_df['trip_id'] == total]
            trip_route = int(trip['route_id'].iloc[0])
            route = self.routes_df.loc[self.routes_df['route_id'] == trip_route]
            route_name = route['route_long_name']
            self.biggest_delay_stop.setText("Biggest delay right now is " + str(biggest//60) + " minutes on route " + str(route_name.iloc[0]))
        else:
            self.biggest_delay_stop.setText("There are no delayed trains at this time")

        self.biggest_delay_stop.move(220, 200)
        self.biggest_delay_stop.resize(400, 100)

    def show_five_stop_delays(self):
        number = 0
        total_delayed = 0
        total = 0
        for delay in self.trip_updates:
            if delay['stop_id'] == str(self.stop_id) and delay['delay'] >= 300:
                number += 1
                total += 1
                total_delayed += 1
            elif delay['stop_id'] == str(self.stop_id) and delay['delay'] > 0:
                total += 1
                total_delayed += 1
            elif delay['stop_id'] == str(self.stop_id):
                total += 1

        if number != 0:
            percentage = number / total
            percentage *= 100
            percentage_delays = number / total_delayed
            percentage_delays *= 100
            self.stop_five_delays.setText("\n" + str(number) + " trains are delayed by more than 5 minutes")
            self.stop_five_delays_percentage.setText(" of total \n ( " + str(int(percentage)) + "% ) ")
            self.stop_five_delays_percentage_delays.setText("of delayed \n ( " + str(int(percentage_delays)) + "% ) ")
        else:
            self.stop_five_delays.setText("There are no delays bigger than 5 minutes at this time")
            self.stop_five_delays_percentage.setText("")
            self.stop_five_delays_percentage_delays.setText("")

        self.stop_five_delays.move(220, 290)
        self.stop_five_delays.resize(300, 100)
        self.stop_five_delays_percentage.move(510, 290)
        self.stop_five_delays_percentage.resize(100, 100)
        self.stop_five_delays_percentage_delays.move(450, 290)
        self.stop_five_delays_percentage_delays.resize(100, 100)


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
            print(f"Erreur lors du traitement du fichier {file_path}: {e}")
            return None

        return feed

    def real_time_gtfs(self):
        self.trip_updates = []
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
