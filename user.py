from .core import get_user_rolename
from .database import UserInfo, add_info

async def binding_role(uid,gid,name: str):
    name_byte = len(name.encode("gbk"))
    if name_byte > 14:
        return f"仅支持14字节以内的ID，目前字节：{name_byte}"

    if not (rid := await get_user_rolename(name)):
        return f"未查询到角色：{name}"

    if await UserInfo.get_info(uid,gid):
        if await UserInfo.set_info(uid,gid,name=name,rid=rid):
            return f"\n角色修改为：\n{name}"
        return "绑定失败"
    await add_info(uid,gid,name,rid)
    return f"\n角色：{name}\n数字ID：{rid}\n绑定成功！"