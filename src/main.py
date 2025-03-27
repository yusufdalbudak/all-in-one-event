import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu,
                           QAction, QTabWidget, QWidget, QVBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from src.event_viewer.event_viewer import EventViewer
from src.event_manager.event_manager import EventManager
from src.utils.logger import setup_logger, log_info, log_error

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All-Event-in-One")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize logger
        self.logger = setup_logger()
        log_info(self.logger, "Application started")
        
        # Initialize system tray
        self.setup_system_tray()
        
        # Initialize main components
        self.setup_ui()
        
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add Event Viewer tab
        self.event_viewer = EventViewer()
        tab_widget.addTab(self.event_viewer, "Event Viewer")
        
        # Add Event Manager tab
        self.event_manager = EventManager()
        tab_widget.addTab(self.event_manager, "Event Manager")
        
        layout.addWidget(tab_widget)
        
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # TODO: Add proper icon
        # self.tray_icon.setIcon(QIcon("path/to/icon.png"))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "All-Event-in-One",
            "Application minimized to tray",
            QSystemTrayIcon.Information,
            2000
        )
        
    def quit_application(self):
        log_info(self.logger, "Application shutting down")
        QApplication.quit()

def check_admin_privileges():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def main():
    # Check for admin privileges
    if not check_admin_privileges():
        print("Warning: Some features may require administrator privileges")
    
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 