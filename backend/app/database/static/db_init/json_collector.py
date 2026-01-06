from typing import Dict, List, Optional

from database.static.db_init.db_init_models import (
    AnyExportJson,
    AnyExportJsonDirect,
    ExportJsonDict,
#    get_exported_json_dict_key,
)


class JsonCollector:
    AVAILABLE_JSON_NAMES: List[str] = [
        "ExportCustoms",
        "ExportDrones",
        "ExportFlavour",
        "ExportFusionBundles",
        "ExportGear",
        "ExportKeys",
        "ExportRecipes",
        "ExportRegions",
        "ExportRelicArcane",
        "ExportResources",
        "ExportSentinels",
        "ExportSortieRewards",
        "ExportUpgrades",
        "ExportWarframes",
        "ExportWeapons",
        "ExportManifest",
    ]

    LANGUAGE_CODE_LIST: List[str] = [
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

    def get_json_index(self, language_code: str) -> Optional[List[str]]:
        url: str = (
            "https://origin.warframe.com/PublicExport/index_"
            + language_code.lower()
            + ".txt.lzma"
        )
        try:
            import requests

            response: requests.Response = requests.get(url, stream=True)
        except Exception as e:
            print(f"[ERROR] While getting index lzma from the Public Export API: {e}")
            return None
        try:
            import lzma

            index_file: bytes = lzma.decompress(response.content)
            index_content: str = index_file.decode("utf-8")
            return index_content.splitlines()
        except Exception as e:
            print(f"[ERROR] While decompressing index lzma: {e}")
            return None

    def get_export_json(
        self, index_content: List[str], json_name: str
    ) -> Optional[dict[str, AnyExportJson]]:
        if json_name != "ExportManifest":
            file_match: str = json_name + "_"
        else:
            file_match: str = json_name + "."
        file_name: str = ""
        for line in index_content:
            if line.startswith(file_match):
                file_name = line
                break
        if len(file_name) == 0:
            print(
                f"[ERROR] No matching json for the name {json_name} in the given index"
            )
            return None
        try:
            import requests

            url: str = "http://content.warframe.com/PublicExport/Manifest/" + file_name
            response: requests.Response = requests.get(url, stream=True)
        except Exception as e:
            print(
                f"[ERROR] While getting json {file_name} from the Public Export API: {e}"
            )
            return None
        try:
            json_res = response.json()
            # return json_res[list(json_res.keys())[0]]
            return json_res
        except Exception as e:
            print(
                f"[ERROR] While loading json {file_name} from the Public Export API as a json: {e}"
            )
            return None
        
    def get_jsons(
        self, language_code: str, json_names: List[str]
    ) -> Optional[ExportJsonDict]:
        if language_code.lower() not in self.LANGUAGE_CODE_LIST:
            print(f"[ERROR] {language_code} is not an accepted language code")
            return None

        for name in json_names:
            if name not in self.AVAILABLE_JSON_NAMES:
                json_names.remove(name)
                print(
                    f"[WARNING] {name} is not an existing json in the Public Export API"
                )
        if len(json_names) == 0:
            print("[ERROR] No json available in the Public Export API were given")
            return None

        index_content = self.get_json_index(language_code)
        if index_content is None:
            return None
        results: ExportJsonDict = {}
        # results = {}
        from concurrent.futures import Future, ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=min(len(json_names), 16)) as executor:
            future_to_index: Dict[Future[Optional[dict[str, AnyExportJson]]], str] = {
                executor.submit(
                    self.get_export_json, index_content, json_name
                ): json_name
                for json_name in json_names
            }

            for future in as_completed(future_to_index):
                name: str = future_to_index[future]
                try:
                    res: dict[str, AnyExportJson] | None = future.result()
                    if isinstance(res, dict):
                        if len(res.keys()) == 1:
                            results[name] = res[
                                next(iter(res))
                            ]
                        else:
                            print(f"[ERROR] Unexpected json with {name}")
                except Exception as e:
                    print(f"[ERROR] downloading {name}:  {e}")

        return results

    def load_json(self, path: str) -> Optional[AnyExportJsonDirect]:
        import json

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {path}")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return None
