from kml.ui import search_window
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from PIL import ImageQt
import os


class MainWindow(QMainWindow):
    def __init__(self, library):
        super(MainWindow, self).__init__()
        self.library = library

        # Setting up Qt's database access objects
        self.qdb = QSqlDatabase.addDatabase('QSQLITE')
        self.qdb.setDatabaseName(os.path.join(library.directory, 'Library.db'))
        self.qdb.open()

        # Creating models for the manga_list_view and chapter_table_view
        self.manga_model = QSqlQueryModel()
        self.manga_model.setQuery('SELECT title FROM manga ORDER BY title')
        self.chapter_model = QSqlQueryModel()

        self.statusBar()

        self.action_exit = QAction('Exit', self)
        self.action_search_new_manga = QAction('Search', self)
        self.action_search_new_manga.triggered.connect(self.search_new_manga_dialog)

        self.file_menu = self.menuBar().addMenu('File')
        self.library_menu = self.menuBar().addMenu('Library')

        self.file_menu.addAction(self.action_exit)
        self.library_menu.addAction(self.action_search_new_manga)

        tool_bar = self.addToolBar('Library')
        tool_bar.addAction(self.action_search_new_manga)

        # Creating Widgets
        self.manga_lv = QListView(self)
        self.manga_lv.setModel(self.manga_model)
        self.manga_lv.selectionModel().selectionChanged.connect(self.on_action_manga_lv)

        self.chapter_tv = QTableView(self)
        self.chapter_tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.chapter_tv.verticalHeader().hide()
        header = self.chapter_tv.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

        self.cover_label = QLabel(self)
        self.cover_label.setMinimumSize(150, 300)

        vbox = QVBoxLayout()
        vbox.addWidget(self.manga_lv)
        vbox.addWidget(self.cover_label)
        vbox.setAlignment(self.cover_label, Qt.AlignCenter)
        vbox.setMargin(0)
        vbox_layout = QWidget()
        vbox_layout.setLayout(vbox)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(vbox_layout)
        splitter.addWidget(self.chapter_tv)
        splitter.setStretchFactor(1, 10)

        self.setCentralWidget(splitter)
        self.setGeometry(0, 0, 1200, 800)
        self._centralize_window()
        self.show()

    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def on_action_manga_lv(self, index):
        self.update_chapter_lv()
        # @TODO: update the cover label
        index = self.manga_lv.selectionModel().currentIndex()
        title = self.manga_lv.model().itemData(index)[0]
        self.cover_label.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(self.library.covers[title]).copy()))

    def update_chapter_lv(self):
        index = self.manga_lv.selectionModel().currentIndex()
        title = self.manga_lv.model().itemData(index)[0]
        cursor = self.library.db.cursor()
        cursor.execute('SELECT id FROM manga WHERE title=\'{}\''.format(title))
        h = cursor.fetchone()
        cmd = 'SELECT title, number, completed, downloaded FROM chapter WHERE manga_id={} ORDER BY number'.format(h[0])
        self.chapter_model.setQuery(cmd)
        self.chapter_tv.setModel(self.chapter_model)

    def update_manga_lv(self):
        self.manga_model.setQuery('SELECT title FROM manga ORDER BY title')
        self.manga_lv.setModel(self.manga_model)

    def search_new_manga_dialog(self):
        self.window = search_window.SearchWindow(self.library, self)
        self.window.show()