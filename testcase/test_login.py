import allure                                  # 导入 allure 库（报告用），之后可以用 allure.xxx
import pytest                                  # 导入 pytest 库，之后可以用 pytest.mark、pytest.param
from common.data_loader import load_cases_from_yaml

@allure.feature("登录模块")                     # 装饰器：给下面这个类打标签，报告里归到「登录模块」
class TestLogin:                               # 定义一个类，名字必须以 Test 开头（pytest 收集规则）

    @allure.story("账号密码登录")                # 装饰器：报告里的子分类
    @allure.title("{case_id}：{title}")         # 装饰器：报告标题，{}里的名字会从参数里取值填入
    @pytest.mark.parametrize(                  # 装饰器：参数化，pytest 核心功能
        "case_id, title, username, password, expect_code",   # 字符串：声明这一组参数有哪些名字
        load_cases_from_yaml("login_data.yaml")
    )
    def test_login(self, case_id, title, username, password, expect_code, anon_client):
        # ↑ self 是类方法的固定第一个参数（Python 规定）
        # ↑ 中间五个参数名，和上面字符串里声明的一一对应
        # ↑ anon_client 是 fixture 名，pytest 看到它会自动注入「未登录的客户端」

        resp = anon_client.post("/login", json={
            "username": username,        # 字典的键是固定的（后端认这个键名），值是参数传进来的变量
            "password": password
        })
        # ↑ 发送 POST 请求，json= 后面跟一个字典，requests 会自动转成 JSON 字符串发给后端
        # ↑ resp 拿到的是 Response 对象

        assert resp.status_code == 200, f"HTTP 失败：{resp.text[:200]}"
        # ↑ assert 断言语句：条件为 True 就放行，为 False 就报错并显示逗号后面的信息
        # ↑ f"..." 是 f-string，{}里的变量会被替换成真实值
        # ↑ resp.text[:200] 是字符串切片：只取前 200 个字符，防止报错信息太长

        body = resp.json()               # 把响应体解析成 Python 字典，存进变量 body
        assert body["code"] == expect_code, \
            f"[{case_id} {title}] 期望 code={expect_code}，实际：{body}"
        # ↑ 行尾的反斜杠 \ 是「续行符」：告诉 Python 这行没写完，和下一行是同一行
        # ↑ body["code"] 用键名从字典里取值
