import win32evtlog
import win32evtlogutil
import win32con
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import Qt, QTimer

class EventViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_event_log()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QVBoxLayout()
        
        # Log type selector
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(['Application', 'Security', 'System'])
        self.log_type_combo.currentTextChanged.connect(self.refresh_events)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh_events)
        
        # Export button
        export_btn = QPushButton('Export to CSV')
        export_btn.clicked.connect(self.export_to_csv)
        
        filter_layout.addWidget(QLabel('Log Type:'))
        filter_layout.addWidget(self.log_type_combo)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addWidget(export_btn)
        
        # Event table
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(5)
        self.event_table.setHorizontalHeaderLabels([
            'Time Generated', 'Source Name', 'Event ID', 'Event Type', 'Message'
        ])
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.event_table)
        self.setLayout(layout)
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_events)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def setup_event_log(self):
        self.server = 'localhost'
        self.log_type = self.log_type_combo.currentText()
        self.hand = win32evtlog.OpenEventLog(self.server, self.log_type)
        self.flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        
    def refresh_events(self):
        self.log_type = self.log_type_combo.currentText()
        self.setup_event_log()
        
        events = []
        while True:
            events_batch = win32evtlog.ReadEventLog(
                self.hand,
                self.flags,
                0
            )
            if not events_batch:
                break
            events.extend(events_batch)
            
        self.display_events(events)
        
    def display_events(self, events):
        self.event_table.setRowCount(len(events))
        
        for row, event in enumerate(events):
            # Time Generated
            time_str = event.TimeGenerated.strftime('%Y-%m-%d %H:%M:%S')
            self.event_table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # Source Name
            self.event_table.setItem(row, 1, QTableWidgetItem(event.SourceName))
            
            # Event ID
            self.event_table.setItem(row, 2, QTableWidgetItem(str(event.EventID)))
            
            # Event Type
            event_type = self.get_event_type(event.EventType)
            self.event_table.setItem(row, 3, QTableWidgetItem(event_type))
            
            # Message
            self.event_table.setItem(row, 4, QTableWidgetItem(str(event.StringInserts)))
            
        self.event_table.resizeColumnsToContents()
        
    def get_event_type(self, event_type):
        event_types = {
            win32evtlog.EVENTLOG_ERROR_TYPE: 'Error',
            win32evtlog.EVENTLOG_WARNING_TYPE: 'Warning',
            win32evtlog.EVENTLOG_INFORMATION_TYPE: 'Information',
            win32evtlog.EVENTLOG_AUDIT_SUCCESS: 'Success Audit',
            win32evtlog.EVENTLOG_AUDIT_FAILURE: 'Failure Audit'
        }
        return event_types.get(event_type, 'Unknown')
        
    def export_to_csv(self):
        data = []
        for row in range(self.event_table.rowCount()):
            row_data = []
            for col in range(self.event_table.columnCount()):
                item = self.event_table.item(row, col)
                row_data.append(item.text() if item else '')
            data.append(row_data)
            
        df = pd.DataFrame(data, columns=[
            'Time Generated', 'Source Name', 'Event ID', 'Event Type', 'Message'
        ])
        
        filename = f'event_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(filename, index=False) 