import yaml
import subprocess
import logging
from datetime import datetime
import os
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox
from PyQt5.QtCore import Qt, QTimer

class RuleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Rule")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        # Rule name
        self.name_edit = QLineEdit()
        layout.addRow("Rule Name:", self.name_edit)
        
        # Event ID
        self.event_id_edit = QLineEdit()
        layout.addRow("Event ID:", self.event_id_edit)
        
        # Source Name
        self.source_edit = QLineEdit()
        layout.addRow("Source Name:", self.source_edit)
        
        # Action type
        self.action_combo = QComboBox()
        self.action_combo.addItems(['Log', 'Command', 'Popup'])
        layout.addRow("Action:", self.action_combo)
        
        # Action parameters
        self.action_param_edit = QLineEdit()
        layout.addRow("Action Parameters:", self.action_param_edit)
        
        # Occurrence count
        self.occurrence_spin = QSpinBox()
        self.occurrence_spin.setRange(1, 100)
        layout.addRow("Occurrence Count:", self.occurrence_spin)
        
        # Time window (minutes)
        self.time_window_spin = QSpinBox()
        self.time_window_spin.setRange(1, 1440)
        layout.addRow("Time Window (minutes):", self.time_window_spin)
        
        # Buttons
        buttons_layout = QVBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addRow("", buttons_layout)
        
        self.setLayout(layout)
        
    def get_rule_data(self):
        return {
            'name': self.name_edit.text(),
            'event_id': self.event_id_edit.text(),
            'source': self.source_edit.text(),
            'action': self.action_combo.currentText(),
            'action_params': self.action_param_edit.text(),
            'occurrence_count': self.occurrence_spin.value(),
            'time_window': self.time_window_spin.value()
        }

class EventManager(QWidget):
    def __init__(self):
        super().__init__()
        self.rules = []
        self.event_history = {}
        self.setup_ui()
        self.load_rules()
        
        # Ensure history directory exists
        if not os.path.exists('history'):
            os.makedirs('history')
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(7)
        self.rules_table.setHorizontalHeaderLabels([
            'Name', 'Event ID', 'Source', 'Action', 'Parameters',
            'Occurrence', 'Time Window'
        ])
        
        # Buttons
        add_btn = QPushButton("Add Rule")
        add_btn.clicked.connect(self.add_rule)
        
        delete_btn = QPushButton("Delete Rule")
        delete_btn.clicked.connect(self.delete_rule)
        
        save_btn = QPushButton("Save Rules")
        save_btn.clicked.connect(self.save_rules)
        
        layout.addWidget(self.rules_table)
        layout.addWidget(add_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)
        
    def add_rule(self):
        dialog = RuleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            rule_data = dialog.get_rule_data()
            self.rules.append(rule_data)
            self.update_rules_table()
            
    def delete_rule(self):
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules.pop(current_row)
            self.update_rules_table()
            
    def update_rules_table(self):
        self.rules_table.setRowCount(len(self.rules))
        for row, rule in enumerate(self.rules):
            self.rules_table.setItem(row, 0, QTableWidgetItem(rule['name']))
            self.rules_table.setItem(row, 1, QTableWidgetItem(rule['event_id']))
            self.rules_table.setItem(row, 2, QTableWidgetItem(rule['source']))
            self.rules_table.setItem(row, 3, QTableWidgetItem(rule['action']))
            self.rules_table.setItem(row, 4, QTableWidgetItem(rule['action_params']))
            self.rules_table.setItem(row, 5, QTableWidgetItem(str(rule['occurrence_count'])))
            self.rules_table.setItem(row, 6, QTableWidgetItem(str(rule['time_window'])))
            
    def load_rules(self):
        try:
            with open('config/rules.yaml', 'r') as f:
                self.rules = yaml.safe_load(f) or []
                self.update_rules_table()
        except FileNotFoundError:
            self.rules = []
            
    def save_rules(self):
        try:
            os.makedirs('config', exist_ok=True)
            with open('config/rules.yaml', 'w') as f:
                yaml.dump(self.rules, f)
        except Exception as e:
            logging.error(f"Error saving rules: {e}")
            
    def check_event(self, event):
        event_key = f"{event.SourceName}_{event.EventID}"
        
        if event_key not in self.event_history:
            self.event_history[event_key] = []
            
        self.event_history[event_key].append(datetime.now())
        
        # Clean old events
        self.clean_event_history()
        
        # Check rules
        for rule in self.rules:
            if (rule['event_id'] == str(event.EventID) and
                rule['source'] == event.SourceName):
                
                if self.check_rule_conditions(rule, event_key):
                    self.execute_action(rule, event)
                    
    def clean_event_history(self):
        current_time = datetime.now()
        for event_key in list(self.event_history.keys()):
            self.event_history[event_key] = [
                t for t in self.event_history[event_key]
                if (current_time - t).total_seconds() < 86400  # 24 hours
            ]
            if not self.event_history[event_key]:
                del self.event_history[event_key]
                
    def check_rule_conditions(self, rule, event_key):
        if event_key not in self.event_history:
            return False
            
        recent_events = self.event_history[event_key]
        time_window = rule['time_window'] * 60  # Convert to seconds
        
        # Count events within time window
        current_time = datetime.now()
        count = sum(1 for t in recent_events
                   if (current_time - t).total_seconds() <= time_window)
                   
        return count >= rule['occurrence_count']
        
    def execute_action(self, rule, event):
        action = rule['action']
        params = rule['action_params']
        
        if action == 'Log':
            self.log_event(event, rule)
        elif action == 'Command':
            self.execute_command(params)
        elif action == 'Popup':
            self.show_popup(params, event)
            
    def log_event(self, event, rule):
        """Log triggered event to CSV file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        event_time = event.TimeGenerated.strftime('%Y-%m-%d %H:%M:%S')
        
        data = {
            'Timestamp': [timestamp],
            'Rule Name': [rule['name']],
            'Event Time': [event_time],
            'Source Name': [event.SourceName],
            'Event ID': [event.EventID],
            'Event Type': [event.EventType],
            'Message': [str(event.StringInserts)]
        }
        
        df = pd.DataFrame(data)
        history_file = f'history/event_history_{datetime.now().strftime("%Y%m%d")}.csv'
        
        # Append to existing file or create new one
        if os.path.exists(history_file):
            df.to_csv(history_file, mode='a', header=False, index=False)
        else:
            df.to_csv(history_file, index=False)
            
    def execute_command(self, command):
        try:
            subprocess.Popen(command, shell=True)
        except Exception as e:
            logging.error(f"Error executing command: {e}")
            
    def show_popup(self, message, event):
        # TODO: Implement popup notification
        pass 