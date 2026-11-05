import pytest
from common.api_client import ApiClient
from config.config import Env

TEST_USER = "testuser"
TEST_PWD = "Test@123456"

# @pytest.fixture(scope="function") # function 就是每个函数各登录一次,条用例前后各一对 SETUP/TEARDOWN。
@pytest.fixture(scope="session")# session 是 SETUP 一次、全部用例共享、TEARDOWN 压尾
def client():
    """全局唯一登录态：整个测试会话只登录一次，所有用例复用 token。"""
    # SETUP  S client
    c = ApiClient()
    resp = c.post("/login", json={
        "username": Env.USERNAME,
        "password": Env.PASSWORD
    })
    body = resp.json()
    assert body["code"] == 200, f"登录失败，响应：{body}"
    c.set_token(body["token"])
    yield c # TEARDOWN S client
    # yield 之后是后置动作：全部用例跑完后执行
    c.post("/logout")


@pytest.fixture(scope="module")
def anon_client():
    """未登录的客户端，专门给登录接口本身的用例用。"""
    return ApiClient()

@pytest.fixture(scope="session",autouse=True)
def ensure_test_account(client):
    rows = client.get("/system/user/list",params={"userName": TEST_USER}).json().get("rows", [])
    if rows:
        uid = rows[0]["userId"]
        client.put(f"/system/user/resetPwd", json={"userId":uid,"password":TEST_PWD,})
    else:
        resp = client.post("/system/user", json={
            "userName": TEST_USER,
            "nickName": "登录测试账号",
            "password": TEST_PWD,
            "deptId": 103,
            "roleIds": [2],
            "status": "0",
        }).json()
        assert resp["code"] == 200, f"初始化测试账号失败：{resp}"

    yield