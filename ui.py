import requests
import threading
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QTextEdit, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QCheckBox, QCompleter
from PyQt5.QtCore import Qt, QStringListModel, QRegularExpression, QTimer, QLoggingCategory
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QLabel,QScrollArea
from PyQt5.QtGui import QPixmap, QValidator, QIntValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPalette, QColor
import requests
import time
import utils
import search as sea
import database as db
import csv
from collections import defaultdict
import sys
import asyncio

# Define colors
BACKGROUND_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
ORANGE_COLOR = "#cc5801"
HIGHLIGHT_COLOR = "#333333"

class ImageUploader(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText('Drag and drop an image \nor click to select')
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; font-size: 24px; border: 2px solid {HIGHLIGHT_COLOR}; padding: 0px;")
        self.clicked = False

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.setPixmap(QPixmap(file_path).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
                    break

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            options = QFileDialog.Options()
            dialog = QFileDialog(self)
            dialog.setWindowTitle("Select an Image")
            dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            dialog.setOptions(options)
            dialog.setFixedSize(800, 600) 
            if dialog.exec_(): 
                file_path = dialog.selectedFiles()[0] 
                self.setPixmap(QPixmap(file_path).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
    
    def clear(self):
        self.setPixmap(QPixmap()) 
        self.setText('Drag and drop an image \nor click to select')

class RandomImageGenerator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.generate_random_image()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored) 

    def generate_random_image(self):
        try:
            QLoggingCategory.setFilterRules("qt.gui.icc.warning=false")
            response = requests.get("https://source.unsplash.com/random")
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.setPixmap(pixmap)
        except Exception as e:
            print(f"Error fetching random image: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.generate_random_image()

def getAddressCSV():
    state_to_cities = defaultdict(lambda: {'code': '', 'cities': set()})
    city_to_states = defaultdict(list)

    with open('csv/kelvins/us_cities.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            state_name = row['STATE_NAME']
            state_code = row['STATE_CODE']
            city = row['CITY']

            state_to_cities[state_name]['code'] = state_code
            state_to_cities[state_name]['cities'].add(city)
            city_to_states[city].append((state_name, state_code))

    states = list(state_to_cities.keys())
    state_codes = [info['code'] for info in state_to_cities.values()]
    cities = list(city_to_states.keys())

    state_to_cities = {state: {'code': info['code'], 'cities': list(info['cities'])} for state, info in state_to_cities.items()}

    return states, state_codes, cities, state_to_cities, city_to_states

class WebCrawlerApp(QWidget):
    states, state_codes, cities, state_to_cities, city_to_states = getAddressCSV()
    sys.argv += ['-platform', 'windows:darkmode=2']

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        
        self.setWindowTitle("Web Crawler")
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        
        self.setGeometry(100, 100, 2800, 1600)  # Set initial window size (x, y, width, height)

        main_layout = QGridLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(30,30,30,30)
        self.setLayout(main_layout)

        font = QFont("Microsoft YaHei Light") 
        first_row = 6
        # Credentials
        credential_frame = QFrame(self)
        credential_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 0px;}};;")
        credential_layout = QGridLayout()
        credential_frame.setLayout(credential_layout)
        credential_layout.setSpacing(0)
        credential_layout.setContentsMargins(0,0,0,0)
        credential_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(credential_frame, 1, 1, first_row, 2) 

        # Credentials Weight
        credential_weight_frame = QFrame(self)
        credential_weight_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 0px;}};")
        credential_weight_layout = QGridLayout()
        credential_weight_frame.setLayout(credential_weight_layout)
        credential_weight_layout.setSpacing(0)
        credential_weight_layout.setContentsMargins(0,0,0,0)
        credential_weight_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(credential_weight_frame, 1, 3, first_row, 1) 
        
        # Images
        image_frame = QFrame(self)
        image_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 0;}};")
        image_layout = QGridLayout()
        image_frame.setLayout(image_layout)
        image_layout.setSpacing(0)
        image_layout.setContentsMargins(0,0,0,0)
        #image_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(image_frame, 1, 4, first_row, 1) 

        # Images Weight
        images_weight_frame = QFrame(self)
        images_weight_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 0px;}};")
        images_weight_layout = QGridLayout()
        images_weight_frame.setLayout(images_weight_layout)
        images_weight_layout.setSpacing(0)
        images_weight_layout.setContentsMargins(0,0,0,0)
        #images_weight_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(images_weight_frame, 1, 5, first_row, 1) 

        # Submit
        submit_frame = QFrame(self)
        submit_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 100px;}};")
        submit_layout = QVBoxLayout()
        submit_frame.setLayout(submit_layout)
        main_layout.addWidget(submit_frame, 1, 6, first_row, 2) 

        
        self.credential_labels = ["Name:", "Birth:", "Phone:", "Address:", "Zipcode:"]
        self.credential_textfields = [["First", "Mid", "Last"], ["D", "M", "Y"], ["", "", ""], ["Street", "City", "State"], ["Zipcode"]]
        self.result_filter_checkboxes = []
        self.credential_entries = []
        self.credential_weights = []

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setVerticalSpacing(1)
        grid_layout.setContentsMargins(0, 10, 20, 0)

        # Validators
        name_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z ]+"))
        birthday_validator = QRegularExpressionValidator(QRegularExpression(r"\d{0,2}"))
        birthyear_validator = QRegularExpressionValidator(QRegularExpression(r"\d{0,4}"))
        phone_validator = QRegularExpressionValidator(QRegularExpression(r"\d{0,3}"))
        phone_base_validator = QRegularExpressionValidator(QRegularExpression(r"\d{0,4}"))
        address_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9 ,.-]+"))
        zipcode_validator = QRegularExpressionValidator(QRegularExpression(r"\d{0,5}"))

   
        
        # Create a completer with both states and abbreviations
        state_completer = QCompleter(self.states + self.state_codes)
        state_completer.setCaseSensitivity(Qt.CaseInsensitive)
        state_completer.setFilterMode(Qt.MatchStartsWith)
        completer_popup = state_completer.popup()
        completer_popup.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR}; padding: 2px;")
        completer_popup.verticalScrollBar().setStyleSheet("QScrollBar::handle:vertical {"
                         "    max-height: 5px;" 
                         "}"
                         "QScrollBar:vertical {"
                         "    border: none;"
                         "    max-width: 10px;"  
                         "}"
                         "QScrollBar::handle:vertical {"
                         f"    color: {ORANGE_COLOR}"
                         "    border: none;"  
                         "}"
                         "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
                         "    border: none;"      
                         "}")
        
        # Create a completer with both states and abbreviations
        city_completer = QCompleter(self.cities)
        city_completer.setCaseSensitivity(Qt.CaseInsensitive)
        city_completer.setFilterMode(Qt.MatchStartsWith)
        completer_popup = city_completer.popup()
        completer_popup.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR}; padding: 2px;")
        completer_popup.verticalScrollBar().setStyleSheet("QScrollBar::handle:vertical {"
                         "    max-height: 5px;" 
                         "}"
                         "QScrollBar:vertical {"
                         "    border: none;"
                         "    max-width: 10px;"  
                         "}"
                         "QScrollBar::handle:vertical {"
                         f"    color: {ORANGE_COLOR}"
                         "    border: none;"  
                         "}"
                         "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
                         "    border: none;"      
                         "}")

        # Credentials
        font = QFont("Sitka Heading Semibold")
        for i, label_text in enumerate(self.credential_labels):
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR}; padding-left: 10px;")
            label.setMaximumHeight(40)  # Set maximum height to 40 pixels
            label.setFont(font)
            label.setAlignment(Qt.AlignVCenter)
            grid_layout.addWidget(label, i, 0, 1, 1, Qt.AlignVCenter)

            for j, text_text in enumerate(self.credential_textfields[i]):
                entry = QLineEdit()
                entry.setPlaceholderText(text_text)
                entry.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; border-radius: 0px; padding: 5px;")
                
                if text_text == "State":
                    entry.setPlaceholderText("State")
                    # Set the completer to the state text field
                    entry.setCompleter(state_completer)
                    self.state_entry = entry
                elif text_text == "City":
                    ## TODO Enter your Code Here:
                    entry.setPlaceholderText("City")
                    entry.setCompleter(city_completer)
                    self.city_entry = entry


                # Apply validators
                elif label_text == "Name:":
                    entry.setValidator(name_validator)
                elif label_text == "Birth:" and j < 2:
                    entry.setValidator(birthday_validator)
                elif label_text == "Birth:" and j == 2:
                    entry.setValidator(birthyear_validator)
                elif label_text == "Phone:" and j < 2:
                    entry.setValidator(phone_validator)
                elif label_text == "Phone:" and j == 2:
                    entry.setValidator(phone_base_validator)
                elif label_text == "Address:":
                    entry.setValidator(address_validator)
                elif label_text == "Zipcode:":
                    entry.setValidator(zipcode_validator)

                if len(self.credential_textfields[i]) < 3:
                    # Zipcode textfield
                    grid_layout.addWidget(entry, i, j+1, 1, 1)
                else:
                    grid_layout.addWidget(entry, i, j+1)
                self.credential_entries.append(entry)

            checkbox = QCheckBox()
            checkbox.setStyleSheet("color: #ffffff;")
            checkbox.stateChanged.connect(self.apply_filters)
            self.result_filter_checkboxes.append(checkbox)
            grid_layout.addWidget(checkbox, i, 5)

        # Event handlers
        self.state_entry.textChanged.connect(self.update_city_completer)
        self.city_entry.textChanged.connect(self.update_state_completer)
        
        # Connect editingFinished signal for state_entry
        self.state_entry.editingFinished.connect(self.autocompleteState)

        # Connect editingFinished signal for city_entry
        self.city_entry.editingFinished.connect(self.autocompleteCity)

        label = QLabel("Credentials")
        label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 40px; border-bottom: 4px solid {ORANGE_COLOR}; padding: 5px;")
        label.setFont(font)
        label.setMaximumHeight(100)

        credential_layout.addWidget(label, 1, 1, 1, 1)
        credential_layout.addLayout(grid_layout, 2, 1, 4, 1)

        # Set the stretch factor to make sure the rows are fixed at 40 pixels height
        for i in range(len(self.credential_labels)):
            grid_layout.setRowStretch(i, 1)
            grid_layout.setRowMinimumHeight(i, 60)

        grid_layout2 = QGridLayout()
        grid_layout2.setHorizontalSpacing(15)
        grid_layout2.setVerticalSpacing(1)
        grid_layout2.setContentsMargins(40,0,40,0)

        # Credentials Weight
        font = QFont("Sitka Heading Semibold")
        for i, label_text in enumerate(self.credential_labels):
            weight_scale = QSlider(Qt.Horizontal)
            weight_scale.setRange(1, 10)
            weight_scale.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; padding: 5px;")
            weight_scale.setStyleSheet(f"QSlider::handle:horizontal {{background-color: {ORANGE_COLOR};}}")
            weight_scale.setMaximumWidth(99900)
            weight_scale.setMinimumHeight(20)
            weight_scale.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set size policy to Fixed
            grid_layout2.addWidget(weight_scale, i, 1)
            self.credential_weights.append(weight_scale)
        label = QLabel("Weight")
        label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 40px; border-bottom: 4px solid {ORANGE_COLOR}; padding: 5px;")
        label.setFont(font)
        label.setMaximumHeight(100)
        credential_weight_layout.addWidget(label, 1,1,1,1)
        credential_weight_layout.addLayout(grid_layout2, 2,1,4,1)

        # Set the stretch factor to make sure the rows are fixed at 40 pixels height
        for i in range(len(self.credential_labels)):
            grid_layout2.setRowStretch(i, 1)
            grid_layout2.setRowMinimumHeight(i, 60)

        # Image
        grid_layout3 = QGridLayout()
        grid_layout3.setVerticalSpacing(0)
        grid_layout3.setContentsMargins(40,0,40,30)

        label = QLabel("Images")
        label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 40px; border-bottom: 4px solid {ORANGE_COLOR}; padding: 5px;")
        label.setFont(font)
        label.setMaximumHeight(100)

        # Image uploader setup
        self.image_uploader = ImageUploader(self)
        #self.image_uploader.setFixedSize(200, 200)  # Set the fixed size as required
        self.image_uploader.setMinimumHeight(240)
        grid_layout3.addWidget(self.image_uploader, 2, 1, 2, 1)
        
        remove_button = QPushButton("Remove Image")
        remove_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 10px;")
        #remove_button.setFixedSize(500, 50)  # Set the fixed size as required
        remove_button.clicked.connect(lambda: self.image_uploader.clear())  # Connect the clicked signal to clear the image uploader
        grid_layout3.addWidget(remove_button, 4, 1, 1, 1)  # Adjust the row according to your layout

        image_layout.addWidget(label, 1,1,1,1, Qt.AlignTop)
        image_layout.addLayout(grid_layout3, 2,1,4,1, Qt.AlignVCenter)


        #Image Weight
        grid_layout4 = QGridLayout()
        #grid_layout4.setHorizontalSpacing(15)
        #grid_layout4.setVerticalSpacing(40)
        grid_layout4.setContentsMargins(40,0,40,0)
        #grid_layout4.setAlignment(Qt.AlignBottom)  
        font = QFont("Sitka Heading Semibold")
        self.weight_scale_uploader = QSlider(Qt.Horizontal)
        self.weight_scale_uploader.setRange(1, 10)
        self.weight_scale_uploader.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; padding: 5px;")
        self.weight_scale_uploader.setStyleSheet(f"QSlider::handle:horizontal {{background-color: {ORANGE_COLOR};}}")
        self.weight_scale_uploader.setMaximumWidth(99900)
        self.weight_scale_uploader.setMinimumHeight(20)
        self.weight_scale_uploader.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
        grid_layout4.addWidget(self.weight_scale_uploader, 2,1)
        label = QLabel("Weight")
        label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 40px; border-bottom: 4px solid {ORANGE_COLOR}; padding: 5px;")
        label.setFont(font)
        label.setMaximumHeight(100)
        images_weight_layout.addWidget(label, 1,1,1,1, Qt.AlignTop)
        images_weight_layout.addLayout(grid_layout4, 2,1,4,1, Qt.AlignVCenter)

        #Submit
        self.submit_button = QPushButton("Submit")
        button_size = 200  # Adjust the size as needed
        self.submit_button.setFixedSize(button_size, button_size)
        self.submit_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 100px; padding: 0px;")
        self.submit_button.clicked.connect(self.submit_credentials)
        submit_layout.addWidget(self.submit_button, 1)
        submit_layout.setAlignment(Qt.AlignHCenter)
        #submit_layout.setContentsMargins(0,100,0,100)


        """
        # Search frame
        search_frame = QFrame(self)
        search_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 20px;}};")
        search_layout = QVBoxLayout()
        search_frame.setLayout(search_layout)
        main_layout.addWidget(search_frame, 1, 5) 

     
        # First row containing search type and advanced search link
        search_type_layout = QHBoxLayout()
        search_layout.addLayout(search_type_layout)
        search_type_layout.setSpacing(50)

        inner_search_type_layout = QHBoxLayout()
        search_type_layout.addLayout(inner_search_type_layout)
        search_type_layout.setAlignment(inner_search_type_layout, Qt.AlignLeft)
        inner_search_type_layout.setSpacing(50)

        # Label to select all
        select_all_label = QLabel("Select All")
        select_all_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR};")
        select_all_label.mousePressEvent = lambda event: self.toggle_search_all()
        inner_search_type_layout.addWidget(select_all_label)

        # Search Option Checkboxes
        self.search_filter_checkboxes = []
        self.search_filter_labels = ["SearchType0", "SearchType1", "SearchType2", "SearchType3", "SearchType4"]
        for label in self.search_filter_labels:
            checkbox = QCheckBox(label)
            checkbox.setStyleSheet(f"color: {TEXT_COLOR};")
            checkbox.stateChanged.connect(self.apply_filters)
            self.search_filter_checkboxes.append(checkbox)
            inner_search_type_layout.addWidget(checkbox,0)

        # Advanced Search Link
        self.advanced_search_link = QLabel(f'<a href="#" style="color: {TEXT_COLOR}; text-decoration: none;">Advanced Search</a>')
        self.advanced_search_link.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR}; padding: 0px;")
        self.advanced_search_link.setMaximumHeight(50)
        self.advanced_search_link.setOpenExternalLinks(False)
        self.advanced_search_link.linkActivated.connect(self.show_advanced_search)
        search_type_layout.addWidget(self.advanced_search_link)

        # Second row containing search bar and stuff
        search_bar_layout = QHBoxLayout()
        search_layout.addLayout(search_bar_layout)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; font-size: 32px; border-radius: 10px; padding: 15px;")
        search_bar_layout.addWidget(self.search_bar, 6)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 15px;")
        self.submit_button.clicked.connect(self.submit_credentials)
        search_bar_layout.addWidget(self.submit_button, 1)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 15px;")
        self.stop_button.clicked.connect(self.stop_searching)
        #search_bar_layout.addWidget(self.stop_button, 1)


        # Advanced Search Pop-up Box
        self.advanced_search_box = QWidget(self)
        self.advanced_search_box.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; border: 0px solid #ff8800; padding: 0px;")
        self.advanced_search_box.setVisible(False)
        advanced_search_layout = QGridLayout()
        advanced_search_layout.setHorizontalSpacing(100)
        self.advanced_search_box.setLayout(advanced_search_layout)
        search_layout.addWidget(self.advanced_search_box)

        
        self.inputs_label = QLabel("Advanced Search")
        self.inputs_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 40px; font-weight: bold;")
        font = QFont("Microsoft YaHei Light")  # Change "Arial" to the desired font family and 12 to the desired font size
        self.inputs_label.setFont(font)
        self.inputs_label.setMaximumHeight(100)
        #advanced_search_layout.addWidget(self.inputs_label)

        self.credential_labels = ["First Name:", "Last Name:", "Phone Number:", "Home Address:", "Hometown:"]
        self.credential_entries = []
        self.credential_weights = []

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        # Credentials
        font = QFont("Sitka Heading Semibold")
        for i, label_text in enumerate(self.credential_labels):
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 32px;")
            label.setFont(font)
            grid_layout.addWidget(label, i, 0)

            entry = QLineEdit()
            entry.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; border-radius: 2px; padding: 5px;")
            grid_layout.addWidget(entry, i, 1)
            self.credential_entries.append(entry)

            weight_label = QLabel("Weight:")
            weight_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 32px;")
            weight_label.setFont(font)
            grid_layout.addWidget(weight_label, i, 2)

            weight_scale = QSlider(Qt.Horizontal)
            weight_scale.setRange(1, 10)
            weight_scale.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR};")
            weight_scale.setStyleSheet(f"QSlider::handle:horizontal {{background-color: {ORANGE_COLOR};}}")
            weight_scale.setMaximumWidth(200)
            grid_layout.addWidget(weight_scale, i, 3)
            self.credential_weights.append(weight_scale)

        advanced_search_layout.addLayout(grid_layout,1,1,3,1)

        # Image uploader setup
        self.image_uploader = ImageUploader(self)
        self.image_uploader.setFixedSize(500, 200)  # Set the fixed size as required
        advanced_search_layout.addWidget(self.image_uploader, 1, 2, 1, 2)
        
        # Weight scaler for the uploader
        weight_label_uploader = QLabel("Weight:")
        weight_label_uploader.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 32px;")
        advanced_search_layout.addWidget(weight_label_uploader, 3, 2, 1, 1)

        self.weight_scale_uploader = QSlider(Qt.Horizontal)
        self.weight_scale_uploader.setRange(1, 10)
        self.weight_scale_uploader.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR};")
        self.weight_scale_uploader.setStyleSheet(f"QSlider::handle:horizontal {{background-color: {ORANGE_COLOR};}}")
        self.weight_scale_uploader.setMaximumWidth(200)
        advanced_search_layout.addWidget(self.weight_scale_uploader, 3, 3, 1, 1)


        remove_button = QPushButton("Remove Image")
        remove_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 10px;")
        remove_button.setFixedSize(500, 50)  # Set the fixed size as required
        remove_button.clicked.connect(lambda: self.image_uploader.clear())  # Connect the clicked signal to clear the image uploader
        advanced_search_layout.addWidget(remove_button, 2, 2, 1, 2)  # Adjust the row according to your layout

        font = QFont("Rockwell Extra Bold")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 10px;")
        self.submit_button.clicked.connect(self.submit_credentials)
        self.submit_button.setMaximumHeight(100)
        self.submit_button.setFont(font)
        #button_layout.addWidget(self.submit_button,3)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(f"background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; border-radius: 10px;")
        self.stop_button.clicked.connect(self.stop_searching)
        self.stop_button.setMaximumHeight(100)
        self.stop_button.setFont(font)
        #button_layout.addWidget(self.stop_button,2)
        advanced_search_layout.addLayout(button_layout,2,1)

        font = QFont("Sitka Heading Semibold")
        
        # Filter Result Frame
        filter_results_frame = QFrame(self)
        filter_results_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; ")
        filter_results_frame.setStyleSheet(f"QFrame {{border: 2px solid {ORANGE_COLOR}; padding: 15px;}};")
        
        filter_results_layout = QVBoxLayout()
        inner_filter_results_layout = QVBoxLayout()
        #filter_results_layout.addLayout(inner_filter_results_layout)
        filter_results_frame.setLayout(filter_results_layout)
        main_layout.addWidget(filter_results_frame, 4,1)
        #filter_results_layout.setAlignment(inner_filter_results_layout, Qt.AlignTop)

        self.filter_results_label = QLabel("Filter Results by:")
        self.filter_results_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 40px; font-weight: bold; border: 0px solid {ORANGE_COLOR};")
        self.filter_results_label.setFont(font)
        self.filter_results_label.setFixedHeight(80)
        filter_results_layout.addWidget(self.filter_results_label, 0)
        #filter_results_layout.setAlignment(self.filter_results_label, Qt.AlignTop)

        inner_widget = QWidget()
        inner_widget.setLayout(inner_filter_results_layout)

        # ScrollArea for Filter
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(f"QScrollArea {{border: 2px solid {HIGHLIGHT_COLOR}; padding: 0px}};")
        scroll_area.setWidget(inner_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(600)
        scroll_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        filter_results_layout.addWidget(scroll_area, 1)
        filter_results_layout.setAlignment(scroll_area, Qt.AlignTop)

        
        self.result_filter_checkboxes = []
        self.result_filter_labels = ["First Name", "Last Name", "Address", "Phone Number", "Relevance"]
        for label in self.result_filter_labels:
            checkbox = QCheckBox(label)
            checkbox.setStyleSheet("color: #ffffff;")
            checkbox.stateChanged.connect(self.apply_filters)
            self.result_filter_checkboxes.append(checkbox)
            inner_filter_results_layout.addWidget(checkbox,0)

        self.filter_results_label = QLabel("AI Generated Results:")
        self.filter_results_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 40px; font-weight: bold; border: 0px solid {ORANGE_COLOR};")
        self.filter_results_label.setFont(font)
        self.filter_results_label.setFixedHeight(80)
        filter_results_layout.addWidget(self.filter_results_label, 0)

        # Creates a layout for the text box and label
        text_box_layout = QVBoxLayout()

        # Creates a text box
        self.ai_text_box = QLabel()
        self.ai_text_box.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; font-size: 28px; line-height: 1.5; border: 2px solid {HIGHLIGHT_COLOR};")
        self.ai_text_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.ai_text_box.setWordWrap(True)
        text_box_layout.addWidget(self.ai_text_box)

        filter_results_layout.addLayout(text_box_layout,2)

        """

        # Result frame for results table
        results_frame = QFrame(self)
        results_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        results_frame.setStyleSheet(f"QFrame {{border: 2px solid {ORANGE_COLOR}; padding: 15px;}};")
        results_layout = QVBoxLayout()
        results_frame.setLayout(results_layout)
        main_layout.addWidget(results_frame, first_row+2,1,16,7)

        # Result Search thing
        filter_frame = QFrame(self)
        filter_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        filter_frame.setStyleSheet(f"QFrame {{border: 2px solid {ORANGE_COLOR}; padding: 0px;}};")
        filter_search_layout = QHBoxLayout()
        filter_search_layout.setAlignment(Qt.AlignLeft)
        filter_frame.setLayout(filter_search_layout)
        main_layout.addWidget(filter_frame, first_row+1,1,1,5)

        filter_search_label = QLabel("Filter Search:")
        filter_search_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR};")
        filter_search_label.setMaximumWidth(400)
        filter_search_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # Set size policy to Minimum for
        filter_search_layout.addWidget(filter_search_label, 1, Qt.AlignLeft)

        # Horizontal layout for search bar and match count label
        self.result_search_bar = QLineEdit()
        self.result_search_bar.setPlaceholderText("Search by URL...")
        self.result_search_bar.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; font-size: 32px; border-radius: 10px; padding: 20px;")
        self.result_search_bar.textChanged.connect(self.apply_filters)
        self.result_search_bar.setFixedWidth(1300)
        filter_search_layout.addWidget(self.result_search_bar, 20, Qt.AlignLeft)
        
        # Result thing by
        filter_by_frame = QFrame(self)
        filter_by_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 0px;")
        filter_search_by_layout = QHBoxLayout()
        filter_search_by_layout.setAlignment(Qt.AlignCenter)  # Align the layout to the center
        filter_by_frame.setLayout(filter_search_by_layout)
        main_layout.addWidget(filter_by_frame, first_row + 1, 6, 1, 2)

        filter_by_label = QLabel("Filter By:")
        filter_by_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR}; padding: 5px;")
        filter_by_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align the label to the right and vertically centered
        filter_search_by_layout.addWidget(filter_by_label)

        self.filter_combo_box = QComboBox()
        self.filter_combo_box.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 32px; border: 2px solid {ORANGE_COLOR}; padding: 5px;")
        self.filter_combo_box.addItems(["Relevance"])
        for label in self.credential_labels:
            self.filter_combo_box.addItem(label.split(":")[0])
        self.filter_combo_box.addItem("Picture")
        self.filter_combo_box.setFixedWidth(400)
        filter_search_by_layout.addWidget(self.filter_combo_box, alignment=Qt.AlignLeft | Qt.AlignVCenter)  # Align the combo box to the left and vertically centered

        self.scroll_positions = {}  # Dictionary to store scroll positions

        font = QFont("Sitka Heading Semibold")
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels(["URL", "Info", "Relevance_score", "Name_relevance_score", "Birthday_relevance_score"," Phone_relevance_score", "Address_relevance_score", "Zipcode_relevance_score", "Picture_relevance_score"])
        # Set the width for each column
        column_widths = [1000,2200,1,1,1,1,1,1,1]  # Example widths for each column
        for i, width in enumerate(column_widths):
            self.results_table.setColumnWidth(i, width)

        
        header = self.results_table.horizontalHeader()
        header.setStyleSheet(f"QHeaderView::section {{ background-color: {ORANGE_COLOR}; font-size: 32px; color: {TEXT_COLOR}; }}")
        header.setFont(font)
        header.setDefaultAlignment(Qt.AlignLeft)
        vheader = self.results_table.verticalHeader()
        vheader.setStyleSheet(f"QHeaderView::section {{ background-color: {ORANGE_COLOR}; font-size: 32px; color: {TEXT_COLOR}; padding: 2px;}}")

        #self.results_table.setStyleSheet(f"QHeaderView::section {{ background-color: {ORANGE_COLOR}; color: {TEXT_COLOR}; }} ")
        self.results_table.setStyleSheet(f"border: 2px solid {HIGHLIGHT_COLOR}; padding: 0px;")
        self.results_table.verticalHeader().setDefaultSectionSize(400)

        header.setSectionResizeMode(QHeaderView.Interactive)  # Set resize mode to Interactive
        results_layout.addWidget(self.results_table)

        # smoothness
        self.results_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.results_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        #Hide
        """
        self.results_table.setColumnHidden(2, True)
        self.results_table.setColumnHidden(3, True)
        self.results_table.setColumnHidden(4, True)
        self.results_table.setColumnHidden(5, True)
        self.results_table.setColumnHidden(6, True)
        self.results_table.setColumnHidden(7, True)
        """

        # Initial state of filters
        self.last_search_text = self.result_search_bar.text()
        self.last_filter_states = [checkbox.isChecked() for checkbox in self.result_filter_checkboxes]
        self.last_db_mtime = db.get_db_mtime()
        self.last_filter_combo_box = self.filter_combo_box.currentIndex()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(1000)

        #self.toggle_search_all()
        #self.update_ai_text(utils.get_random_fact())
    
    def autocompleteState(self):
        text = self.state_entry.text().strip()
        if text:
            completer = self.state_entry.completer()
            if completer.popup().isVisible():
                current_completion = completer.currentCompletion()
                if current_completion:
                    self.state_entry.setText(current_completion)

    def autocompleteCity(self):
        text = self.city_entry.text().strip()
        if text:
            completer = self.city_entry.completer()
            if completer.popup().isVisible():
                current_completion = completer.currentCompletion()
                if current_completion:
                    self.city_entry.setText(current_completion)

    # Function to get the state name and code for a given city
    def get_states_for_city(self, city):
        return self.city_to_states.get(city, [(None, None)])

    # Function to get the list of cities and state code for a given state
    def get_cities_for_state(self, state):
        state_info = self.state_to_cities.get(state, {"code": None, "cities": []})
        return state_info['code'], state_info['cities']
    
    def update_city_completer(self, text):
        # Check if the input text matches any state name or state code
        valid_state = None
        for state in self.states:
            if text.lower() == state.lower() or text.lower() == self.state_to_cities[state]['code'].lower():
                valid_state = state
                break

        if valid_state:
            state_code, cities = self.get_cities_for_state(valid_state)
            self.city_entry.completer().setModel(QStringListModel(cities))
        else:
            self.city_entry.completer().setModel(QStringListModel(self.cities))

    def update_state_completer(self, text):
        # Get all possible states and codes for the given city text
        possible_states = self.get_states_for_city(text)
        state_names = [state[0] for state in possible_states]
        state_codes = [state[1] for state in possible_states]

        if possible_states:
            self.state_entry.completer().setModel(QStringListModel(state_names + state_codes))
        else:
            self.state_entry.completer().setModel(QStringListModel(self.states + self.state_codes))


    def update_ai_text(self, new_text):
        print("hi")
        #self.ai_text_box.setText("<p style='line-height: 150%;'>"+new_text+"</p>")   

    # Function to toggle select all checkboxes
    def toggle_search_all(self):
        isAllChecked = True;
        for checkbox in self.search_filter_checkboxes:
            if not checkbox.isChecked():
                isAllChecked = False
                break

        for checkbox in self.search_filter_checkboxes:
            checkbox.setChecked(True)
            if isAllChecked:
                checkbox.setChecked(False)
            

    def show_advanced_search(self):
        self.advanced_search_box.setVisible(not self.advanced_search_box.isVisible())

    def submit_credentials(self):
        db.clear_database()
        """
        if (self.advanced_search_box.isVisible()):
            inputs = [entry.text() for entry in self.credential_entries]
            weights = [scale.value() for scale in self.credential_weights]
            inputs.append(utils.pixmap_to_png_bytes(self.image_uploader.pixmap()))
            weights.append(self.weight_scale_uploader.value())
            inputs.insert(0, '')
            weights.insert(0, 0)

        else:    
            inputs = [self.search_bar.text()]
            weights = [1]
            for i in range(5):
                inputs.append('')
                weights.append(0)
            inputs.append(b'')
            weights.append(0)
        """
        inputs = []
        weights = []
        inputs = [entry.text() for entry in self.credential_entries]
        weights = [scale.value() for scale in self.credential_weights]
        inputs.append(utils.pixmap_to_png_bytes(self.image_uploader.pixmap()))
        weights.append(self.weight_scale_uploader.value())
        #[["First", "Mid", "Last"], ["D", "M", "Y"], ["", "", ""], ["Street", "City", "Aprt"], ["Town"]]
        
        search_query = sea.Search(inputs, weights)    
        """
        for i in range(5):
            if self.search_filter_checkboxes[i].isChecked():
                self.searching_flag = True
                threading.Thread(target=self.crawl_web, args=(i,), kwargs={'search_query': search_query}).start()
        """
        #threading.Thread(target=self.crawl_web, args=(0,), kwargs={'search_query': search_query}).start()
        threading.Thread(target=self.crawl_web, args=(0,), kwargs={'search_query': search_query}).start()
        #self.crawl_web(1, kwargs={'search_query': search_query})
        
    def apply_filters(self):
        search_text = self.result_search_bar.text().lower()
        match_count = 0
        for row in range(self.results_table.rowCount()):
            show_row = True
            url_item = self.results_table.item(row, 0)
            if url_item is None or search_text not in url_item.text().lower():
                show_row = False
            #self.filter_combo_box.currentText()
            for col, checkbox in enumerate(self.result_filter_checkboxes):
                if checkbox.isChecked():
                    item = self.results_table.item(row, col + 3)  # Skip URL column
                    if item is None or int(item.text()) == 0:
                        show_row = False
                        break

            self.results_table.setRowHidden(row, not show_row)
            if show_row:
                match_count += 1
                
            sort = self.filter_combo_box.currentIndex() + 2
            self.results_table.sortItems(sort, Qt.DescendingOrder)
        
        #self.match_count_label.setText(f"{match_count} Matches Found")

    def crawl_web(self, search_type, **kwargs):
        search_query = kwargs.get('search_query')

        if (search_type == 0):
            sea.SearchType0.search(self, search_query)
        if (search_type == 1):
            sea.SearchType1.search(self, search_query)
        if (search_type == 2):
            sea.SearchType2.search(self, search_query)
        if (search_type == 3):
            sea.SearchType3.search(self, search_query)
        if (search_type == 4):
            sea.SearchType4.search(self, search_query)

    def check_for_updates(self):
        current_db_mtime = db.get_db_mtime()
        current_search_text = self.result_search_bar.text()
        current_filter_states = [checkbox.isChecked() for checkbox in self.result_filter_checkboxes]
        current_filter_combo_box = self.filter_combo_box.currentIndex()
        margin_of_relief = 5
        # Check if the database modification time or filters have changed
        if (abs(current_db_mtime - self.last_db_mtime) > margin_of_relief or 
            current_search_text != self.last_search_text or 
            current_filter_combo_box != self.last_filter_combo_box or
            current_filter_states != self.last_filter_states):
            
            self.update_ui()
            
            # Update the last known states
            self.last_db_mtime = current_db_mtime
            self.last_search_text = current_search_text
            self.last_filter_states = current_filter_states
            self.last_filter_combo_box = current_filter_combo_box
    
    def update_ui(self):
        documents = db.fetch_documents_from_db()

        # Save the current scroll positions
        for row in range(self.results_table.rowCount()):
            text_edit = self.results_table.cellWidget(row, 1)
            if text_edit:
                self.scroll_positions[row] = text_edit.verticalScrollBar().value()

        self.results_table.setRowCount(len(documents))
        rows = []
        for doc in documents:
            #combined_value = f"{doc[1]} - {doc[2]}"
            row = [doc[0], doc[1], doc[2], doc[3], doc[4], doc[5], doc[6], doc[7], doc[8]]
            rows.append(row)

        self.results_table.setHorizontalHeaderLabels(["URL", "Info"])
        for row_position, row_data in enumerate(rows):
            for column_position, value in enumerate(row_data):
                if column_position == 1:  
                    text_edit = QTextEdit()
                    text_edit.setHtml(value.replace('\n', '<br>'))
                    text_edit.setStyleSheet("border: none;") 
                    text_edit.setReadOnly(True)
                    text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
                    text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    item = QTableWidgetItem()
                    self.results_table.setItem(row_position, column_position, item)
                    self.results_table.setCellWidget(row_position, column_position, text_edit)
                    if row_position in self.scroll_positions:
                        text_edit.verticalScrollBar().setValue(self.scroll_positions[row_position])

                else:
                    item = QTableWidgetItem(value)
                    self.results_table.setItem(row_position, column_position, item)
        
        self.scroll_positions.clear() 
        self.apply_filters()
