"""
Utility functions untuk export subscriber data
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any


def ensure_output_dir(output_dir: str) -> None:
    """Memastikan output directory ada"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def export_to_json(data: List[Dict[str, Any]], filepath: str) -> None:
    """Export data ke JSON file"""
    ensure_output_dir(os.path.dirname(filepath) if os.path.dirname(filepath) else ".")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data berhasil diexport ke: {filepath}")


def export_to_csv(data: List[Dict[str, Any]], filepath: str) -> None:
    """Export data ke CSV file"""
    if not data:
        print("⚠️ Tidak ada data untuk diexport")
        return
    
    ensure_output_dir(os.path.dirname(filepath) if os.path.dirname(filepath) else ".")
    
    # Ambil semua keys dari data pertama sebagai header
    fieldnames = list(data[0].keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Data berhasil diexport ke: {filepath}")


def format_datetime(timestamp: str) -> str:
    """Format ISO timestamp menjadi format yang lebih readable"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp


def get_timestamp() -> str:
    """Mendapatkan timestamp untuk naming file"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')

