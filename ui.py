import requests
import threading
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QCheckBox
from PyQt5.QtCore import Qt, QTimer, QLoggingCategory
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QLabel,QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
import requests
import time
import utils
import search as sea
import database as db

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


class WebCrawlerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.searching_flag = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Web Crawler Prototype")
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        self.setGeometry(100, 100, 2800, 1600)  # Set initial window size (x, y, width, height)

        main_layout = QGridLayout()
        main_layout.setSpacing(100)
        main_layout.setContentsMargins(100,60,100,60)
        self.setLayout(main_layout)

        # Search frame
        search_frame = QFrame(self)
        search_frame.setStyleSheet(f"QFrame {{background-color: {BACKGROUND_COLOR}; border: 2px solid {ORANGE_COLOR}; padding: 20px;}};")
        search_layout = QVBoxLayout()
        search_frame.setLayout(search_layout)
        main_layout.addWidget(search_frame, 1, 5) 

        # RANDOM IMAGE
        random_image = RandomImageGenerator()
        #random_image.setFixedSize(600, 500)
        main_layout.addWidget(random_image, 1, 1)

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

        # Result frame for results table
        results_frame = QFrame(self)
        results_frame.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        results_frame.setStyleSheet(f"QFrame {{border: 2px solid {ORANGE_COLOR}; padding: 15px;}};")
        results_layout = QVBoxLayout()
        results_frame.setLayout(results_layout)
        main_layout.addWidget(results_frame, 4,5)

        # Horizontal layout for search bar and match count label
        result_search_layout = QHBoxLayout()

        self.result_search_bar = QLineEdit()
        self.result_search_bar.setPlaceholderText("Search by URL...")
        self.result_search_bar.setStyleSheet(f"background-color: {HIGHLIGHT_COLOR}; color: {TEXT_COLOR}; font-size: 32px; border-radius: 10px; padding: 20px;")
        self.result_search_bar.textChanged.connect(self.apply_filters)
        result_search_layout.addWidget(self.result_search_bar)

        self.match_count_label = QLabel("0 Matches Found")
        self.match_count_label.setStyleSheet(f"color: {ORANGE_COLOR}; font-size: 32px; border: 0px solid {ORANGE_COLOR};")
        result_search_layout.addWidget(self.match_count_label)

        results_layout.addLayout(result_search_layout)

        font = QFont("Sitka Heading Semibold")
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["URL", "First Name", "Last Name", "Address", "Phone Number", "Relevance"])
        # Set the width for each column
        column_widths = [600, 200, 200, 300, 400, 200]  # Example widths for each column
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

        header.setSectionResizeMode(QHeaderView.Interactive)  # Set resize mode to Interactive
        results_layout.addWidget(self.results_table)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        self.toggle_search_all()
        self.update_ai_text(utils.get_random_fact())
        
    def update_ai_text(self, new_text):
        self.ai_text_box.setText("<p style='line-height: 150%;'>"+new_text+"</p>")   

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
        
        search_query = sea.Search(inputs, weights)    

        for i in range(5):
            if self.search_filter_checkboxes[i].isChecked():
                self.searching_flag = True
                threading.Thread(target=self.crawl_web, args=(i,), kwargs={'search_query': search_query}).start()

    def apply_filters(self):
        search_text = self.result_search_bar.text().lower()
        match_count = 0
        for row in range(self.results_table.rowCount()):
            show_row = True
            url_item = self.results_table.item(row, 0)
            if url_item is None or search_text not in url_item.text().lower():
                show_row = False

            for col, checkbox in enumerate(self.result_filter_checkboxes):
                if checkbox.isChecked():
                    item = self.results_table.item(row, col + 1)  # Skip URL column
                    if item is None or item.text() == "":
                        show_row = False
                        break

            self.results_table.setRowHidden(row, not show_row)
            if show_row:
                match_count += 1
        
        self.match_count_label.setText(f"{match_count} Matches Found")


    def stop_searching(self):
        self.searching_flag = False
        self.update_ai_text(utils.get_random_fact())
    
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

    def update_ui(self):
        documents = db.fetch_documents_from_db()

        self.results_table.setRowCount(len(documents))
        rows = []
        for doc in documents:
            row = [str(value) for value in doc]
            rows.append(row)

        self.results_table.setHorizontalHeaderLabels(["URL", "First Name", "Last Name", "Address", "Phone Number", "Relevance"])
        for row_position, row_data in enumerate(rows):
            for column_position, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                self.results_table.setItem(row_position, column_position, item)
        
        self.apply_filters()