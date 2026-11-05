import time
import pytest
import allure

@allure.feature("用户管理模块")
class TestUser:
    @allure.story("新增用户-反向校验")
    @allure.title("{case_id}:{title}")
    @pytest.mark.parametrize("case_id,title,field,value,expect_code",[
        pytest.param("u101", "账号为空串", "userName", "", 500, id="101-空账号"),
        pytest.param("u102", "账号31位超长", "userName", "a" * 31, 500, id="102-超长账号"),
        pytest.param("u103", "账号30位边界", "userName", "a" * 30, 200, id="103-30位边界"),
        pytest.param("u104", "手机号格式非法", "phonenumber", "12345", 500, marks=pytest.mark.xfail(reason="缺陷：后端不校验手机号格式",strict = False),id="104-非法手机"),
        pytest.param("u104b", "手机号超长（12位）", "phonenumber", "138001380001", 500,
                     id="104b-手机号超长"),
        pytest.param("u105", "邮箱格式非法", "email", "abc@", 500, id="105-非法邮箱"),
        pytest.param("u106", "密码为空字符串", "password", "", 500, marks=pytest.mark.xfail(reason="缺陷：password无必填校验",strict = False) , id="106-空密码")
    ])
    def test_case_user_invalid(self,case_id,title,field,value,expect_code,client):
        uname = f"autotest_{int(time.time() * 1000)}"
        payload = {
            "userName":uname,
            'nickName':uname,
            "password": "Test@123456",
            "deptId": 103,  # 研发部门（SQL 脚本里确认过的值）
            "roleIds": [2],  # 普通角色
        }
        payload[field] = value

        try:
            body = client.post("/system/user",json=payload).json()
            assert body["code"] == expect_code,\
            f"[{case_id}{title}]期望{expect_code},实际：{body}"
        finally:
            rows = client.get("/system/user/list",params = {"nickName":uname}).json().get("rows",[])
            for row in rows:
                client.delete("/system/user/{uid}".format(uid=row["userId"]),)

    @allure.story("用户修改")
    @allure.title("修改昵称后详细返回新值")
    def test_update_nickname(self,client, temp_user):
        # temp_user 就是那个完整用户 dict
        resp = client.put("/system/user", json={
            "userId": temp_user["userId"],
            "userName": temp_user["userName"],   # 修改接口 userName 必填
            "nickName": "改过的昵称",
        })
        assert resp.json()["code"] == 200, f"修改失败：{resp.text}"

    @allure.story("用户查询")
    @allure.title("按用户名查询，返回唯一记录")
    def test_list_by_username(self,client, temp_user):
        rows = client.get("/system/user/list",
                          params={"userName": temp_user["userName"]}).json()["rows"]
        assert len(rows) == 1

    @allure.story("用户删除")
    @allure.title("删除后列表查不到，落库标记已删除")
    def test_delete_user(self,client, temp_user):
        uid = temp_user["userId"]

        before = client.get(f"/system/user/{uid}").json()
        assert before["code"] == 200,f"前置失败，用户不存在{before}"

        resp = client.delete(f"/system/user/{uid}")
        assert resp.json()["code"] == 200,f"删除失败{resp.text}"

        rows = client.get("/system/user/list",
                          params={"userName": temp_user["userName"]}).json().get("rows", [])
        assert len(rows) == 0, f"删除后仍能查到：{rows}"

        resp2 = client.get(f"/system/user/{temp_user['userId']}")
        assert resp2.json()["code"] == 200
        assert resp2.json()["data"]["delFlag"] == '2',f"没有标记删除:"

