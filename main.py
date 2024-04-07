from hoshino import Service,priv
import re
import traceback

from .update.json import update_equip, update_hero

from .database import UserInfo,init
from .draw import draw_jjc_info, draw_mini_info
from .user import binding_role
from .core import *
import nonebot
nonebot.on_startup(init)
from .config.config import get_config
max_page = min(get_config('max_page'), 8)
image_config = get_config('image')
font_name = image_config['font_name']
image_enable = image_config['enable']

sv = Service('300hero_record', help_='''
[jjc 角色名] 查询角色战绩
             
'''.strip())

@sv.on_rex(re.compile(r'^(zc|jjc)胜场(\S*)$'))
async def _(bot, ev):
    try:
        match = ev['match']
        gid = int(ev.group_id)
        print(match)
        if not (match_id := await match_type(match[1])):
            await bot.send(ev, '未知的比赛类型',at_sender=True)
            return
        if not (user_name := match[2]):
            print(f'user_name:{user_name}')
            uid = int(ev.user_id)
            for i in ev.message:
                if i.type == 'at':
                    uid = int(i.data['qq'])
            if user := await UserInfo.get_info(uid,gid):
                user_name = user.name
            else:
                await bot.send(ev, '未查询到角色绑定信息',at_sender=True)
                return
        if match_wincount := await get_match_wincount(user_name,match_id):
            await bot.send(ev, f"\n角色:{user_name}\n最后对局:{match_wincount[3]}\n今日胜场:{match_wincount[0]}\n击杀:{match_wincount[1]}\t死亡:{match_wincount[2]}",at_sender=True)
        else:
            await bot.send(ev, '角色不存在',at_sender=True)
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev, '查询失败',at_sender=True)
        return
    
# @sv.on_rex(re.compile(r'^(jjc)详情([1-9])(\S*)$'))
# async def _(bot, ev):
#     try:
#         match = ev['match']
#         gid = int(ev.group_id)
#         print(match)
#         if not (match_id := await match_type(match[1])):
#             await bot.send(ev, '未知的比赛类型',at_sender=True)
#             return
#         if not (user_name := match[3]):
#             uid = int(ev.user_id)
#             for i in ev.message:
#                 if i.type == 'at':
#                     uid = int(i.data['qq'])
#             if user := await UserInfo.get_info(uid,gid):
#                 user_name = user.name
#             else:
#                 await bot.send(ev, '未查询到角色绑定信息',at_sender=True)
#                 return
#         if match_number := int(match[2]):
#             if match_number > max_page:
#                 await bot.send(ev, f'请输入{max_page}以内的序号',at_sender=True)
#                 return
#         else:
#             await bot.send(ev, '请输入查询的比赛序号',at_sender=True)
#             return
#         if match_info := await get_match_detail_info(user_name,match_id,match_number):
#             msg = await image_to_base64(await create_image_with_text(match_info.strip()))
#             await bot.send(ev, msg, at_sender=True)
#         else:
#             await bot.send(ev, '查询失败',at_sender=True)
#         return
#     except Exception:
#         traceback.print_exc()
#         await bot.send(ev, '查询失败',at_sender=True)
#         return
    
# @sv.on_rex(re.compile(r'^(jjc)测试([1-9])(\S*)$'))
@sv.on_rex(re.compile(r'^(jjc)详情([1-9])(\S*)$'))
async def _(bot, ev):
    try:
        match = ev['match']
        gid = int(ev.group_id)
        rid = None
        print(match)
        if not (match_id := await match_type(match[1])):
            await bot.send(ev, '未知的比赛类型',at_sender=True)
            return
        if not (user_name := match[3]):
            uid = int(ev.user_id)
            for i in ev.message:
                if i.type == 'at':
                    uid = int(i.data['qq'])
            if user := await UserInfo.get_info(uid,gid):
                user_name = user.name
                rid = user.rid
            else:
                await bot.send(ev, '未查询到角色绑定信息',at_sender=True)
                return
        if match_number := int(match[2]):
            if match_number > max_page:
                await bot.send(ev, f'请输入{max_page}以内的序号',at_sender=True)
                return
        else:
            await bot.send(ev, '请输入查询的比赛序号',at_sender=True)
            return
        if image_enable:
            if not (match_info := await get_match_detail_info(user_name,match_id,match_number,only_json=True,rid=rid)):
                await bot.send(ev, '查询失败',at_sender=True)
                return
            if not (msg := await draw_jjc_info(match_info)):
                msg = '图片生成失败'
        else:
            if not (match_info := await get_match_detail_info(user_name,match_id,match_number,rid=rid)):
                await bot.send(ev, '查询失败',at_sender=True)
                return
            msg = await image_to_base64(await create_image_with_text(match_info.strip(),font_name))
        await bot.send(ev, msg, at_sender=True)
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev, '查询失败',at_sender=True)
        return

@sv.on_rex(re.compile(r'^(jjc)(\S*)$'))
async def _(bot, ev):
    try:
        match = ev['match']
        gid = int(ev.group_id)
        print(match)
        if not (match_id := await match_type(match[1])):
            await bot.send(ev, '未知的比赛类型',at_sender=True)
            return
        rid = None
        if not (user_name := match[2]):
            print(f'user_name:{user_name}')
            uid = int(ev.user_id)
            for i in ev.message:
                if i.type == 'at':
                    uid = int(i.data['qq'])
            print(f'uid:{uid}')
            if user := await UserInfo.get_info(uid,gid):
                user_name = user.name
                rid = user.rid
            else:
                await bot.send(ev, '未查询到角色绑定信息',at_sender=True)
                return
        if not (match_list := await get_match_info(user_name,match_id,1,image_enable,rid)):
            await bot.send(ev, '查询失败',at_sender=True)
            return 
        if image_enable:
            if not (msg := await draw_mini_info(match_list)):
                msg = '图片生成失败'
        else:
            msg = await image_to_base64(await create_image_with_text(f"角色:{user_name}\n{match_list.strip()}",font_name))
        await bot.send(ev, msg, at_sender=True)     
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev, '查询失败',at_sender=True)
        return
    
@sv.on_prefix(('绑定角色'))
async def _(bot, ev):
    try:
        uid = int(ev.user_id)
        gid = int(ev.group_id)
        if name := str(ev.message):
            msg = await binding_role(uid,gid,name)
            await bot.send(ev,msg,at_sender=True)
        else:
            await bot.send(ev,"请输入角色名",at_sender=True)
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev,"绑定失败",at_sender=True)
        return
      
@sv.on_rex('(开启|关闭)自动推送')
async def _(bot, ev):
    try:
        uid = int(ev.user_id)
        gid = int(ev.group_id)
        setup = ev['match'].group(1)
        for i in ev.message:
            if i.type == 'at':
                if not priv.check_priv(ev, priv.ADMIN):
                    await bot.finish(ev, '更改他人推送仅限管理员操作', at_sender=True)
                    return
                uid = int(i.data['qq'])
        auto = bool(auto := ev['match'].group(1) == '开启')
        if user_info := await UserInfo.get_info(uid,gid):
            if not user_info.rid:
                await bot.send(ev,"请先绑定角色",at_sender=True)
                return
            if user_info.auto == auto:
                await bot.send(ev,f'目前已经是{setup}状态了',at_sender=True)
                return 
            user_name = user_info.name
            if await UserInfo.set_info(uid,gid,auto=auto):
                await bot.send(ev,f'角色:{user_name}\n自动推送{setup}成功',at_sender=True)
        else:
            await bot.finish(ev,"未查询到角色绑定信息",at_sender=True)
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev, '查询失败',at_sender=True)
        return

@sv.on_prefix(('查看角色'))
async def _(bot, ev):
    try:
        if ev.message[0].type == 'at':
            uid = int(ev.message[0].data['qq'])
        else:
            uid = int(ev.user_id)
        gid = int(ev.group_id)
        if user := await UserInfo.get_info(uid,gid):
            msg = f'\n角色名:{user.name}\n'
            if user.rid:
                msg += f'数字ID:{user.rid}\n'
            await bot.send(ev,f'\n角色名为:{user.name}\n',at_sender=True)
        else:
            await bot.send(ev,"未查询到角色绑定信息",at_sender=True)
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev,"查询失败",at_sender=True)
        return
    
@sv.on_prefix(('更新300英雄数据'))
async def _(bot, ev):
    try:
        await update_hero()
        await update_equip()
        await bot.send(ev,"300英雄数据更新成功",at_sender=True)
        return
    except Exception:
        traceback.print_exc()
        await bot.send(ev,"300英雄数据更新失败",at_sender=True)
        return
    
@sv.scheduled_job('cron', minute='*/15')
async def auto_info():
    bot = nonebot.get_bot()
    try:
        if not (user_data := await UserInfo.get_all()):
            return None
        gid_groups = {}
        for user in user_data:
            if user['gid'] in gid_groups:
                gid_groups[user['gid']].append(user)
            else:
                gid_groups[user['gid']] = [user]

        # 在每个 gid 组内按 rid 分组，并将 uid 收集到列表中，保持 last_mid 相同
        final_groups = {}
        for gid, users in gid_groups.items():
            gid_group = {}
            for user in users:
                rid = user['rid']
                if rid in gid_group:
                    # 添加 uid 到列表中
                    gid_group[rid]['uid'].append(user['uid'])
                else:
                    # 初始化 rid 组
                    gid_group[rid] = {
                        'uid': [user['uid']],
                        'last_mid': user['last_mid'],
                        'name': user['name']
                    }
            final_groups[gid] = gid_group
        for gid, current_group in final_groups.items():
            print("当前的 gid 是:", gid)
            for rid, user_group in current_group.items():
                print("当前的 rid 是:", rid)
                print("当前 rid 下的用户信息:", user_group)
                uid_list = user_group['uid']
                last_mid = user_group['last_mid']
                name = user_group['name']

                # 获取最新的 mid
                if not (new_mid := await check_last_mid(rid,last_mid)):
                    return None

                # 更新数据库
                await UserInfo.set_mid(uid_list,gid,last_mid=new_mid)

                # 获取最新的对局信息
                if not (match_info := await get_match_detail(new_mid)):
                    return None

                # 绘制图片
                if not (msg := await draw_jjc_info(match_info)):
                    return None
                
                # 发送消息
                send_msg = ''.join(f'[CQ:at,qq={uid}]' for uid in uid_list)
                send_msg += f'角色:{name}\n最新对局:\n{msg}'
                await bot.send_group_msg(group_id=gid, message=send_msg)

    except Exception:
        traceback.print_exc()
        return None