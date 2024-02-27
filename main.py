from hoshino import Service
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
[zc/jjc 角色名] 查询角色战绩
             
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
            if not (match_info := await get_match_detail_info(user_name,match_id,match_number,only_json=True)):
                await bot.send(ev, '查询失败',at_sender=True)
                return
            if not (msg := await draw_jjc_info(match_info)):
                msg = '图片生成失败'
        else:
            if not (match_info := await get_match_detail_info(user_name,match_id,match_number)):
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
        if not (user_name := match[2]):
            print(f'user_name:{user_name}')
            uid = int(ev.user_id)
            for i in ev.message:
                if i.type == 'at':
                    uid = int(i.data['qq'])
            print(f'uid:{uid}')
            if user := await UserInfo.get_info(uid,gid):
                user_name = user.name
            else:
                await bot.send(ev, '未查询到角色绑定信息',at_sender=True)
                return
        if not (match_list := await get_match_info(user_name,match_id,1,image_enable)):
            await bot.send(ev, '查询失败',at_sender=True)
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
    
@sv.on_prefix(('查看角色'))
async def _(bot, ev):
    try:
        if ev.message[0].type == 'at':
            uid = int(ev.message[0].data['qq'])
        else:
            uid = int(ev.user_id)
        gid = int(ev.group_id)
        if user := await UserInfo.get_info(uid,gid):
            await bot.send(ev,f'\n角色名为:{user.name}',at_sender=True)
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