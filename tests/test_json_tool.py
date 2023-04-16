import os
from src.json_tool import json_tool

def test_dump_n_load():
    data = {"apple": 1, "banana": "hello", "c": "ㄜ"}
    json_tool.dump('test.json', data)
    assert json_tool.load('test.json') == data
    os.remove('test.json')
