from datetime import datetime, timezone, timedelta
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json
import httpx
import traceback

from config.config import get_config
from update.headers import record_headers
from update.json import hero_save_path

record_url = get_config('record_url')
rolename_url = record_url.get('rolename',None)
match_list_url = record_url.get('match_list',None)
match_info_url = record_url.get('match_info',None)
max_page = get_config('max_page')

with open(hero_save_path, 'r', encoding='utf-8') as f:
    hero_json = json.load(f)

async def get_hero_name(hero_id):
    return next((i['name'] for i in hero_json if i['id'] == hero_id), None)

async def get_user_rolename(rolename):
    try:
        data = {
            'AccountID': 0,
            'Guid': 0,
            'RoleName': rolename
        }
        print(f'data:{data}')
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url=rolename_url,data=data,headers=record_headers)
            print(f'response:{response}')
        return int(response.json()['data']['RoleID'])
    except Exception:
        traceback.print_exc()
        return None


async def get_user_match_list(RoleID,match_type=1,match_index=1):
    try:
        url = record_url.get('match_list',None)
        data ={
            'RoleID': RoleID,
            'MatchType': match_type,
            'searchIndex': match_index
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url=match_list_url,data=data,headers=record_headers)
        match_data = response.json()['data']['Matchs']['Matchs']
        match_list =[]
        for i in match_data:
            UsedTime = int(i['UsedTime']/60)
            CreateTime = int(i['CreateTime'])
            MTID = str(i['MTID'])
            user_data = i['Players'][0]
            Assist = int(user_data['Assist'])
            KillPlayer = int(user_data['KillPlayer'])
            KillUnit = int(user_data['KillUnit'])
            TotalMoney = await num2k(int(user_data['TotalMoney']))
            Death = int(user_data['Death'])
            FV = int(user_data['FV']) #tuanfen
            PlayerName = str(user_data['RN'])
            MakeDamagePercent = user_data['MakeDamagePercent']
            TotalMoneyPercent = user_data['TotalMoneyPercent']

            # 计算百分比并格式化
            MakeDamagePercent_formatted = "{:.2f}".format(MakeDamagePercent * 100).rstrip('0').rstrip('.')
            TotalMoneyPercent_formatted = "{:.2f}".format(TotalMoneyPercent * 100).rstrip('0').rstrip('.')

            # 计算伤害转换比，确保分母不为零
            if TotalMoneyPercent > 0:
                Damage_Money = "{:.2f}".format((MakeDamagePercent / TotalMoneyPercent) * 100).rstrip('0').rstrip('.')
            else:
                Damage_Money = "0"  # 或者定义为None或其他表示无效的值
            Result = int(user_data['Result'])
            hero_hurt = await num2k(int(user_data['MD'][-1]))
            hero_bear = await num2k(int(user_data['TD'][-1]))
            HeroID = int(user_data['HeroID'])
            HeroLv = int(user_data['HeroLv'])
            json_data = {
                'hero': HeroID,
                'MTID':MTID,
                'lv': HeroLv,
                'kill': KillPlayer,
                'assist': Assist,
                'death': Death,
                'hero_hurt': hero_hurt,
                'hero_bear': hero_bear,
                'kill_unit': KillUnit,
                'money': TotalMoney,
                'result': Result,
                'match_time': UsedTime,
                'match_date': CreateTime,
                'user_name': PlayerName,
                'FV':FV,
                'Damage_Money':Damage_Money,
                'MakeDamagePercent':MakeDamagePercent_formatted,
                'TotalMoneyPercent':TotalMoneyPercent_formatted
            }
            match_list.append(json_data)
        return match_list
    except Exception:
        traceback.print_exc()
        return None
    
#获取详细比赛内容
async def get_match_detail(mtid):
    try:
        data = {
            'mtid': mtid
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url=match_info_url,data=data,headers=record_headers)
        return response.json()['data']
    except Exception:
        traceback.print_exc()
        return None
    
async def get_match_detail_info(rolename,match_type=1,number=1):
    try:
        if not (RoleID := await get_user_rolename(rolename)):
            return None
        
        data ={
            'RoleID': RoleID,
            'MatchType': match_type,
            'searchIndex': 1
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url=match_list_url,data=data,headers=record_headers)
        match_data = response.json()['data']['Matchs']['Matchs']
        MTID = match_data[number-1]['MTID']
        if not (detail_data := await get_match_detail(MTID)):
            return None
        CreateTime = datetime.fromtimestamp(int(detail_data['CreateTime'])).strftime('%Y-%m-%d %H:%M:%S')
        UsedTime = int(detail_data['UsedTime']/60)
        
        text = f"\n对局时间:{CreateTime} 用时:{UsedTime}分\n"
        Players = detail_data['Players']
        for index,i in enumerate(Players):
            Assist = int(i['Assist'])
            KillPlayer = int(i['KillPlayer'])
            KillUnit = int(i['KillUnit'])
            TotalMoney = await num2k(int(i['TotalMoney']))
            Death = int(i['Death'])
            PlayersFV = int(i['FV']) #tuanfen
            PlayerName = str(i['RN'])
            MakeDamagePercent = i['MakeDamagePercent']
            TotalMoneyPercent = i['TotalMoneyPercent']

            # 计算百分比并格式化
            MakeDamagePercent_formatted = "{:.2f}".format(MakeDamagePercent * 100).rstrip('0').rstrip('.')
            TotalMoneyPercent_formatted = "{:.2f}".format(TotalMoneyPercent * 100).rstrip('0').rstrip('.')

            # 计算伤害转换比，确保分母不为零
            if TotalMoneyPercent > 0:
                Damage_Money = "{:.2f}".format((MakeDamagePercent / TotalMoneyPercent) * 100).rstrip('0').rstrip('.')
            else:
                Damage_Money = "0"  # 或者定义为None或其他表示无效的值
            Result = int(i['Result'])
            hero_hurt = await num2k(int(i['MD'][-1]))
            hero_bear = await num2k(int(i['TD'][-1]))
            HeroID = int(i['HeroID'])
            HeroLv = int(i['HeroLv'])
            if not (hero := await get_hero_name(HeroID)):
                hero = '未知英雄'
            result = '胜' if Result == 1 else '负'
            text += f'玩家{index+1}:{PlayerName} 竞技力:{PlayersFV}\n({result}){hero} lv{HeroLv} {KillPlayer}/{Death}/{Assist}/{KillUnit}\n金钱:{TotalMoney} 伤害:{hero_hurt} 承伤:{hero_bear}\n伤害占比:{MakeDamagePercent_formatted}% 经济占比:{TotalMoneyPercent_formatted}% 伤害转换比:{Damage_Money}%\n\n'
        return text
    except Exception:
        traceback.print_exc()
        return None

async def num2k(num):
    num = int(num)
    return str(num) if num < 1000 else '{:.1f}k'.format(num / 1000)


async def send_user_match_info(match_list,match_type=1):
    try:
        match_date = datetime.fromtimestamp(match_list[0]['match_date']).strftime('%Y-%m-%d %H:%M:%S')
        FV = match_list[0]['FV']
        text = f'最后对局:{match_date}\n竞技力:{FV}\n'
        for index,i in enumerate(match_list):
            if index >= max_page:
                break
            result = '胜' if i['result'] == 1 else '负'
            hero_bear = i['hero_bear']
            hero_hurt = i['hero_hurt']
            death = i['death']
            assist = i['assist']
            kill = i['kill']
            match_time = i['match_time']
            if not (hero := await get_hero_name(i['hero'])):
                hero = '未知英雄'
            if match_type != 2:
                lv = i['lv']
                kill_unit = i['kill_unit']
                money = i['money']
                Damage_Money = i['Damage_Money']
                MakeDamagePercent= i['MakeDamagePercent']
                TotalMoneyPercent= i['TotalMoneyPercent']
                text += f'{index+1}.({result}){hero} lv{lv} {kill}/{death}/{assist}/{kill_unit}\n金钱:{money} 伤害:{hero_hurt} 承伤:{hero_bear} 时长:{match_time}分\n伤害占比:{MakeDamagePercent}% 经济占比:{TotalMoneyPercent}% 伤害转换比:{Damage_Money}%\n\n'
            else:
                text += f'{index+1}.({result}){hero} {kill}/{death}/{assist}\n伤害:{hero_hurt} 承伤:{hero_bear} 时长:{match_time}分\n'
        return text
    except Exception:
        traceback.print_exc()
        return None

async def get_match_info(rolename,match_type=1,match_index=1):
    try:
        if not (RoleID := await get_user_rolename(rolename)):
            return None
        match_list = await get_user_match_list(RoleID,match_type,match_index)
        if not match_list:
            return None
        return await send_user_match_info(match_list,match_type)
    except Exception:
        traceback.print_exc()
        return None
    
async def get_match_wincount(rolename,match_type=1):
    try:
        if not (RoleID := await get_user_rolename(rolename)):
            return None
        win_count = 0
        kill = 0
        death = 0
        last_match_date = None
        for index in range(1,10):
            if not (match_list := await get_user_match_list(RoleID,match_type,index)):
                return None
            if index == 1:
                last_match_date = datetime.fromtimestamp(match_list[0]['match_date']).strftime('%Y-%m-%d %H:%M:%S')
            for i in match_list:
                match_date = i['match_date']
                if not await check_today(match_date):
                    return win_count,kill,death,last_match_date
                if i['result'] == 1:
                    win_count += 1
                kill += i['kill']
                death += i['death']
    except Exception:
        traceback.print_exc()
        return None

async def check_today(unix_timestamp):
    # 设置中国时区
    china_timezone = timezone(timedelta(hours=8))

    # 获取中国当前的日期时间
    now_in_china = datetime.now(china_timezone)
    today_date_in_china = now_in_china.date()

    # 将Unix时间戳转换为中国时区的日期
    date_from_timestamp = datetime.fromtimestamp(int(unix_timestamp), china_timezone).date()

    return today_date_in_china == date_from_timestamp

async def match_type(match_type):
    if match_type == 'zc':
        return 2
    elif match_type == 'jjc':
        return 1
    elif match_type == 'sdz':
        return 4
    elif match_type == 'pw':
        return 3
    else:
        return None

async def create_image_with_text(text, font_path='msyh.ttc', font_size=20, padding=10):
    # 创建一个足够大的画布以容纳文本
    image = Image.new('RGB', (800, 600), color = (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 加载字体
    font = ImageFont.truetype(font_path, font_size)

    # 计算文本尺寸
    text_width, text_height = draw.textsize(text, font=font)

    # 调整图片大小，加上一些边距
    image = image.resize((text_width + padding * 2, text_height + padding * 2))

    draw = ImageDraw.Draw(image)
    # 绘制文本，并使其在画布上居中
    draw.text((padding, padding), text, fill=(0, 0, 0), font=font)
    
    return image

async def image_to_base64(pil_image):
    # 创建一个BytesIO对象
    img_buffer = BytesIO()

    # 将图片保存到BytesIO对象中（格式可以是PNG，JPEG等）
    pil_image.save(img_buffer, format='JPEG')

    # 获取BytesIO对象的字节数据
    byte_data = img_buffer.getvalue()

    # 对字节数据进行base64编码
    base64_str = f'base64://{base64.b64encode(byte_data).decode()}'

    # 将编码后的字节数据转换为字符串
    return f'[CQ:image,file={base64_str}]'