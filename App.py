from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap
import sys

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Dashboard"
        self.left = 150
        self.top = 124
        self.width = 1600
        self.height = 720
        self.initUI()
        self.current_date = "30/03/2023"

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


    def check_stop(self,search_bar):
        # checks if the stop name is in the db, for now it only works with "Gare du Nord" write it as it is 
        self.stop = self.search_bar.text()  # gets text from the search bar
        self.test_list = ["Gare du Nord"]   # turn this into actual data
        if self.stop in self.test_list:
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
        self.stop_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fill the available space

        self.stop_title = QLabel(self.stop_window)
        self.stop_title.resize(300, 40)
        self.stop_title.setText(self.search_bar.text())  #Stop name as title
        self.stop_title.setFont(QFont("Arial", 16))
        self.stop_title.move(740, 20)


        self.stop_window.show()

    def new_date(self, modification):
        # move from day to day, get real data instead of "next date" etc
        if modification == 1:
            self.date.setText("next date")
        else:
            self.date.setText("previous date")



def main():
    app = QApplication(sys.argv)
    App()
    sys.exit(app.exec_())

main()