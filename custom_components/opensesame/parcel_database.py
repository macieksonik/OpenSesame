import datetime
import json
from typing import List, Dict, Optional


class ParcelDatabase:
    def __init__(self, data_file: str) -> None:
        self._data_file = data_file
        self._data = self._load_data()

    def _load_data(self) -> List[Dict[str, str]]:
        try:
            with open(self._data_file, "r") as f:
                content = f.read()
                if not content:
                    return []
                return json.loads(content)
        except FileNotFoundError:
            return []

    def count_unchecked_parcels(self) -> int:
        return len([parcel for parcel in self._data if not parcel.get("picked")])

    def get_unchecked_parcels(self) -> List[str]:
        return [parcel["number"] for parcel in self._data if not parcel.get("picked")]

    def add_parcel(self, parcel_number: str) -> None:
        self._data.append({"number": parcel_number, "picked": None})
        self._save_data()

    def del_parcel(self, parcel_number: str) -> bool:
        parcel_to_delete = None

        for parcel in self._data:
            if parcel["number"] == parcel_number:
                parcel_to_delete = parcel
                break

        if not parcel_to_delete:
            return False

        self._data.remove(parcel_to_delete)
        self._save_data()
        return True

    def check_parcel(self, parcel_number: str) -> bool:
        current_time = datetime.datetime.now()
        parcel_to_check = None

        for parcel in self._data:
            if parcel["number"] == parcel_number and not parcel.get("picked"):
                parcel_to_check = parcel
                break

        if not parcel_to_check:
            return False

        if parcel_to_check["picked"] is None or (
            current_time -
                datetime.datetime.fromisoformat(parcel_to_check["picked"])
        ).total_seconds() >= 300:
            parcel_to_check["picked"] = current_time.isoformat()
            self._save_data()
            return True

        return False

    def _save_data(self) -> None:
        with open(self._data_file, "w") as f:
            json.dump(self._data, f)
