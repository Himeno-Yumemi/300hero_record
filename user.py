from .database import UserInfo, add_info

async def binding_role(uid,gid,name: str):
    name_byte = len(name.encode("gbk"))
    if name_byte > 14:
        return f"仅支持14字节以内的ID，目前字节：{name_byte}"
    if await UserInfo.get_info(uid,gid):
        return (
            f"\n角色修改为：\n{name}"
            if await UserInfo.set_info(uid,gid,name=name)
            else "绑定发生错误"
        )
    await add_info(uid,gid,name)
    return f"\n角色：{name}\n绑定成功！"