import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class DataLogger:
    def __init__(self, filename: str = "data/emotion_data.csv"):
        """Initialize with automatic directory creation"""
        self.filename = filename
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self._ensure_header()

    def _ensure_header(self):
        """Create file with headers if doesn't exist"""
        if not Path(self.filename).exists():
            with open(self.filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'username', 'emotion', 'response', 'confidence'])

    def log(self, data: Dict[str, Any]) -> bool:
        """Log emotion data with timestamp"""
        try:
            with open(self.filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    data.get('username', ''),
                    data.get('emotion', ''),
                    data.get('response', ''),
                    data.get('confidence', 0)
                ])
            return True
        except Exception as e:
            print(f"Logging error: {e}")
            return False

    def get_data(self) -> List[Dict[str, str]]:
        """Return all logged data as list of dictionaries"""
        try:
            with open(self.filename, 'r') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []

    def get_user_data(self, username: str) -> List[Dict[str, str]]:
        """Get data for specific user"""
        all_data = self.get_data()
        return [row for row in all_data if row.get('username') == username]

    def clear_user_data(self, username: str) -> bool:
        """Clear data for specific user"""
        try:
            all_data = self.get_data()
            user_data = [row for row in all_data if row.get('username') != username]
            
            with open(self.filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'username', 'emotion', 'response', 'confidence'])
                writer.writeheader()
                writer.writerows(user_data)
            return True
        except Exception as e:
            print(f"Error clearing user data: {e}")
            return False