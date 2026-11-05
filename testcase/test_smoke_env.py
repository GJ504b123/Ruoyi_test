def test_token_valid_http(client):
    """验证 session 级 fixture：登录态可用，token 有效"""
    # 1. http 状态
    resp = client.get("/getInfo")
    assert resp.status_code == 200, f"HTTP 失败，响应：{resp.text[:200]}"
    # 2. 业务码
    body = resp.json()
    assert body["code"] == 200, f"token 校验失败，响应：{body}"
    assert body["user"]["userName"] == "admin"
def test_get_router(client):
    # 1. http 状态
    resp = client.get("/getRouters")
    # 200 OK 写在第一行的状态行里，status_code从来不在 JSON 里。
    assert resp.status_code == 200, f"HTTP 失败，响应：{resp.text[:200]}"
    # 2. 业务码
    body = resp.json()
    assert body["code"] == 200, f"token 校验失败，响应：{body}"
    # 3. 数据结构（data列表非空）
    data = body.get("data", [])
    assert len(data) > 0
    # 4. 业务数据（admin可以看见系统管理菜单）
    menu_title = [menu["meta"]["title"] for menu in data]
    assert "系统管理" in menu_title, f"缺少系统管理系统管理菜单，实际菜单：{menu_title}"