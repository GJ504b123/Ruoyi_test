import requests
import allure
import json
from config.config import Env

class ApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = Env.BASE_URL

    def set_token(self, token: str):
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def request(self, method, url, **kwargs):
        # 用 allure.step 把一次请求变成报告里的一个可折叠步骤
        with allure.step(f"{method} {url}"):
            # 请求体（只有 POST/PUT 有，用 get 取避免 KeyError）
            if kwargs.get("json") is not None:
                allure.attach(
                    json.dumps(kwargs["json"], ensure_ascii=False, indent=2),
                    name="请求体",
                    attachment_type=allure.attachment_type.JSON,
                )

            resp = self.session.request(method, self.base_url + url, **kwargs)

            # 完整响应文本，格式化后挂上去
            allure.attach(
                resp.text,
                name=f"响应（HTTP {resp.status_code}）",
                attachment_type=allure.attachment_type.JSON,
            )
            return resp

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def delete(self,url,**kwargs):
        return self.request("DELETE", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)
