import json
import lzma
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, TypeVar

import requests

T = TypeVar("T")


class JsonCollector:
    BASE_URL = "http://content.warframe.com/PublicExport/Manifest/"
    INDEX_URL = "https://origin.warframe.com/PublicExport/index_"

    LANGUAGE_CODE_LIST = [
        "de",
        "en",
        "es",
        "fr",
        "it",
        "ja",
        "ko",
        "pl",
        "pt",
        "ru",
        "tc",
        "th",
        "tr",
        "uk",
        "zh",
    ]

    def __init__(self):
        self.session = requests.Session()

    def _fetch_lzma_index(self, language_code: str) -> List[str]:
        """Fetches and decompresses the manifest index."""
        url = f"{self.INDEX_URL}{language_code.lower()}.txt.lzma"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            index_file = lzma.decompress(response.content)
            return index_file.decode("utf-8").splitlines()
        except Exception as e:
            print(f"[ERROR] Failed to fetch index for {language_code}: {e}")
            return []

    def get_export_json(
        self, index_content: List[str], json_name: str
    ) -> Optional[Any]:
        """Finds the filename in index and fetches the JSON content."""
        # Manifest is the only one ending in .json instead of _<hash>.json
        file_match = (
            json_name + "." if json_name == "ExportManifest" else json_name + "_"
        )

        file_name = next(
            (line for line in index_content if line.startswith(file_match)), None
        )

        if not file_name:
            print(f"[ERROR] No match for {json_name}")
            return None

        try:
            url = self.BASE_URL + file_name
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            # 1. If it's a list (like ExportManifest), return it directly
            if isinstance(data, list):
                return data

            # 2. If it's a dictionary, handle the nesting
            if isinstance(data, dict):
                # Priority 1: Check if the specific json_name is a key in the dict
                # (e.g., data["ExportWarframes"] -> [...])
                if json_name in data:
                    return data[json_name]

                # Priority 2: Fallback to the "single key" unwrap if it doesn't match the name
                if len(data) == 1:
                    return next(iter(data.values()))

            # 3. Return as-is if it's already unwrapped or has multiple complex keys
            return data

        except Exception as e:
            print(f"[ERROR] Failed fetching {json_name}: {e}")
            return None

    def get_jsons(self, language_code: str, json_names: List[str]) -> Dict[str, Any]:
        """Parallel fetcher for multiple JSON exports."""
        if language_code.lower() not in self.LANGUAGE_CODE_LIST:
            print(f"[ERROR] Invalid language: {language_code}")
            return {}

        index_content = self._fetch_lzma_index(language_code)
        if not index_content:
            return {}

        results: Dict[str, Any] = {}

        workers = min(len(json_names), 10)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_name = {
                executor.submit(self.get_export_json, index_content, name): name
                for name in json_names
            }

            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[name] = data
                except Exception as e:
                    print(f"[ERROR] Exception in thread for {name}: {e}")

        return results

    def save_to_disk(
        self, data_dict: Dict[str, Any], output_dir: str = "./data/json"
    ) -> bool:
        try:
            os.makedirs(output_dir, exist_ok=True)
            for name, content in data_dict.items():
                path = os.path.join(output_dir, f"{name}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                print(f"[INFO] Saved {path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save JSONs: {e}")
            return False
