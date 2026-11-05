import time

import pytest

@pytest.fixture
def temp_user(client):
    username = f"autotest_{int(time.time() * 1000)}"
    resp = client.post("/system/user", json={
        "userName": username,
        "nickName": "自动化测试用户",
        "password": "Test@123456",
        "deptId": 103,  # 研发部门（SQL 脚本里确认过的值）
        "roleIds": [2],  # 普通角色

    })
    body = resp.json()
    assert body["code"] == 200,f"新增用户失败：{body}"

    # 查询
    resp = client.get("/system/user/list", params={"userName": username})
    body = resp.json()
    rows = body.get("rows",[])
    try:
        assert len(rows) == 1,f"应该查到1条，实际:{rows}"
        user = rows[0]
        yield user
    finally:
        resp = client.delete(f"/system/user/{user["userId"]}")
        assert resp.json()["code"] == 200, f"清理测试用户失败：{resp.text}"