import json
import base64


class JsonTool:
    def dump(self, save_path: str, result: dict):
        json_str = bytes(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
        en_json_strs = map(base64.b64encode, json_str.split(b"\n"))
        with open(save_path, "wb") as f:
            for string in en_json_strs:
                f.write(string + b"\n")
            print(save_path, "saved")

    def load(self, load_path: str) -> dict:
        json_strs = []
        with open(load_path, "rb") as f:
            for string in f:
                json_strs.append(base64.b64decode(string))
            result = json.loads(b"\n".join(json_strs))
        return result

    @staticmethod
    def _dump_original(save_path, result):
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


json_tool = JsonTool()
