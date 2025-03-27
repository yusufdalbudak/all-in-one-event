# All-Event-in-One-Module

A comprehensive Windows Event Management System that integrates Event Viewer and System Event Management functionalities.

## Features

- Real-time Windows Event Log monitoring
- Customizable event management rules
- GUI-based rule builder
- System tray support
- Email notifications
- Log export capabilities
- Audit logging

## Requirements

- Windows 10/11
- Python 3.8 or higher
- Administrator privileges (for certain operations)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/all-in-one-event.git
cd all-in-one-event
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

## Project Structure

```
all-in-one-event/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/                 # GUI components
│   ├── event_viewer/        # Event viewer module
│   ├── event_manager/       # Event management module
│   ├── rule_editor/         # Rule editor module
│   └── utils/               # Utility functions
├── config/                  # Configuration files
├── logs/                    # Application logs
└── tests/                   # Test files
```

## License

MIT License 