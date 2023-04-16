import json
from cryptography.fernet import Fernet

key = Fernet.generate_key()


class JsonTool:
    def __init__(self, key_path: str):
        try:
            with open(key_path, "rb") as filekey:
                key = filekey.read()
            self._fernet = Fernet(key)
        except:
            print("no encrypt/decrypt function")

    def dump(self, save_path: str, result: dict):
        json_str = bytes(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
        en_json_str = self._fernet.encrypt(json_str)
        with open(save_path, "wb") as f:
            f.write(en_json_str)
            print(save_path, "saved")

    def load(self, load_path: str) -> dict:
        with open(load_path, "rb") as f:
            json_str = self._fernet.decrypt(f.read())
            result = json.loads(json_str)
        return result

    @staticmethod
    def _dump_original(save_path, result):
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


json_tool = JsonTool("filekey.key")
