""""从yaml文件加载测试数据"""

from pathlib import Path
import pytest
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
def load_cases_from_yaml(file_name:str):
    yaml_path = ROOT_DIR/ "data"/ file_name
    with open(yaml_path,encoding="utf-8") as f:
        raw = yaml.safe_load(f) # yaml加载的safe版本

    cases = []
    for item in raw:
        marks = [pytest.mark.smoke] if item.get("-") else []
        cases.append(pytest.param(
            item["case_id"],
            item["title"],
            item["username"],
            item["password"],
            item["expect_code"],
            marks = marks,
            id = item.get("id",item["case_id"]),
        )),
    return cases