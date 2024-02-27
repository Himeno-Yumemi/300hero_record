import os
import random
import time
import traceback
from PIL import Image, ImageDraw, ImageFont

from .core import get_hero_name,image_to_base64,num2k,get_hero_head,get_equip_path
from .config.config import get_config

image_config = get_config('image')
font_name = image_config['font_name']

image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'image')
font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),font_name)

async def get_random_skin():
    try:
        skin_dir = os.path.join(image_dir, 'ui/icon/skin')
        # 筛选出所有纯数字的文件夹
        hero_dirs = [d for d in os.listdir(skin_dir) if d.isdigit()]
        if not hero_dirs:
            return None  # 如果没有找到纯数字的文件夹，返回None
        
        hero_dir = random.choice(hero_dirs)
        hero_path = os.path.join(skin_dir, hero_dir)
        # 从选定的文件夹中筛选出符合条件的.bmp文件
        skin_list = [file for file in os.listdir(hero_path) if file.count('_') == 1 and file.endswith('.bmp')]
        
        if not skin_list:
            return None  # 如果没有找到符合条件的.bmp文件，返回None
        
        return os.path.join(hero_path, random.choice(skin_list))
    except Exception:
        traceback.print_exc()
        return None

async def draw_jjc_info(json_data):
    Player_Data = json_data['Players']
    max_attempts = 10
    attempts = 0

    background = None
    while not background and attempts < max_attempts:
        if background := await get_random_skin():
            break
        attempts += 1

    if not background:
        return None

    original_img = Image.open(background)

    # 计算缩放后的尺寸
    new_height = 1080
    new_width = int(1080 * original_img.width / original_img.height)

    # 进行等比缩放
    img = original_img.resize((new_width, new_height))
    overlay = Image.new('RGBA', (new_width, new_height), (255, 255, 255,0))
    
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, new_width, new_height), fill=(255, 255, 255 ,150))
    UsedTime = max(int(json_data['UsedTime']) //60,1)
    CreateTime = time.strftime("%Y - %m - %d    %H : %M : %S", time.localtime(int(json_data['CreateTime'])))

    font = ImageFont.truetype(font_path, 22)
    font2 = ImageFont.truetype(font_path, 24)

    time_font = ImageFont.truetype(font_path, 20)
    
    draw.rectangle((0, 0, new_width, 30), fill=(255, 255, 255,50))
    draw.text((10, 0), f'{CreateTime}', fill=(255,255,255), font=time_font,stroke_fill=(0, 0, 0),stroke_width=2)
    draw.text((300, 0), f'用时:{UsedTime}分', fill=(255,255,255), font=time_font,stroke_fill=(0, 0, 0),stroke_width=2)
    time_line_spacing = 30
    new_height = new_height - time_line_spacing
    
    for index,item in enumerate(Player_Data):
        HeroID = int(item['HeroID'])
        if not (hero := await get_hero_name(HeroID)):
            hero = '未知英雄'
        HeroLv = int(item['HeroLv'])
        RN = item['RN']
        FV = int(item['FV'])
        Ep = item['Ep']
        KillPlayer = int(item['KillPlayer'])
        Death = int(item['Death'])
        Assist = int(item['Assist'])
        KillUnit = int(item['KillUnit'])
        Result = item['Result']
        TotalMoney = int(item['TotalMoney'])
        MakeDamagePercent_formatted = "{:.2f}".format(item['MakeDamagePercent'] * 100).rstrip('0').rstrip('.')
        TotalMoneyPercent_formatted = "{:.2f}".format(item['TotalMoneyPercent'] * 100).rstrip('0').rstrip('.')
        DamageConversionRate = "{:.2f}".format(item['DamageConversionRate'] * 100).rstrip('0').rstrip('.')
        KDA = "{:.2f}".format((KillPlayer + Assist) / max(Death,1)).rstrip('0').rstrip('.')
        hero_hurt = await num2k(int(item['MD'][-1]))
        hero_bear = await num2k(int(item['TD'][-1]))
        info_data = f'{KillPlayer}/{Death}/{Assist}/{KillUnit}'
        hurt_bear = f'伤:{hero_hurt} 承:{hero_bear}'
        
        once_line_spacing = int(new_height//14)
        line_spacing = time_line_spacing+once_line_spacing*index
        result_line_spacing = time_line_spacing+once_line_spacing*(index+1)   

        if Result == 1:
            draw.rectangle((0, line_spacing, 48, result_line_spacing), fill=(0, 255, 0,60))
        elif Result == 2:
            draw.rectangle((0, line_spacing, 48, result_line_spacing), fill=(255, 0, 0,60))
        _, text_height = draw.textsize(f'{HeroLv}', font=font)
        _, text2_height = draw.textsize(f'{HeroLv}', font=font2,stroke_width=2)
        font_up_line_spacing = once_line_spacing //2 - text_height
        font_down_line_spacing = once_line_spacing //2
        font2_line_spacing = (once_line_spacing - text2_height) // 2

        image_line_spacing = (once_line_spacing - 64) // 2


        # 将HeroID和HeroLv绘制到画布上
        draw.text((10, font2_line_spacing+line_spacing), f'{HeroLv}', fill=(255,255,255), font=font2,stroke_fill=(0, 0, 0),stroke_width=2)
        overlay = await draw_image_on_canvas(overlay, HeroID, (60, image_line_spacing+line_spacing), 'hero')
        draw.text((150, font_up_line_spacing+line_spacing), f'{hero}', fill=(0, 0, 0), font=font)
        draw.text((150, font_down_line_spacing+line_spacing), f'{RN}', fill=(0, 0, 0), font=font)

        
        draw.text((330, font2_line_spacing+line_spacing), f'分:{FV}', fill=(0, 0, 0), font=font2)

        SummonerSkill1 = int(item['SummonerSkill1'])
        SummonerSkill2 = int(item['SummonerSkill2'])
        overlay = await draw_image_on_canvas(overlay,SummonerSkill1,(440, image_line_spacing+line_spacing),'skill')
        overlay = await draw_image_on_canvas(overlay,SummonerSkill2,(505, image_line_spacing+line_spacing),'skill')

        for EP_index,EP_item in enumerate(Ep):
            # 单数跳过
            if EP_index % 2:
                continue
            if EP_item := int(EP_item):
                overlay = await draw_image_on_canvas(overlay,EP_item,(int(610 + EP_index / 2 * 65), image_line_spacing + line_spacing),'equipment')
               
        draw.text((1560, font2_line_spacing+line_spacing), f'评分:{KDA}', fill=(0, 0, 0), font=font2)
        
        draw.text((1050, font_up_line_spacing+line_spacing), info_data, fill=(0, 0, 0), font=font)
        draw.text((1050, font_down_line_spacing+line_spacing), hurt_bear, fill=(0, 0, 0), font=font)

        
        draw.text((1250, font_up_line_spacing+line_spacing), f'{TotalMoney}', fill=(0, 0, 0), font=font)
        draw.text((1250, font_down_line_spacing+line_spacing), f'{TotalMoneyPercent_formatted}%', fill=(0, 0, 0), font=font)

        draw.text((1360, font_up_line_spacing+line_spacing), f'伤害占比:{MakeDamagePercent_formatted}%', fill=(0, 0, 0), font=font)
        draw.text((1360, font_down_line_spacing+line_spacing), f'伤害转换:{DamageConversionRate}%', fill=(0, 0, 0), font=font
                # ,stroke_width=2,stroke_fill=(255,255,255)
                  )
        if index == 6:
            draw.line((0, result_line_spacing, new_width, result_line_spacing), fill=(0, 0, 0), width=3)
        else:
            draw.line((0, result_line_spacing, new_width, result_line_spacing), fill=(0, 0, 0), width=1)
    img.paste(overlay, (0, 0), overlay)
    return await image_to_base64(img)

async def draw_mini_info(json_data):
    max_attempts = 10
    attempts = 0

    background = None
    while not background and attempts < max_attempts:
        if background := await get_random_skin():
            break
        attempts += 1

    if not background:
        return None
    original_img = Image.open(background)

    # 计算缩放后的尺寸
    new_height = 1080
    new_width = int(new_height * original_img.width / original_img.height)

    # 进行等比缩放
    img = original_img.resize((new_width, new_height))
    overlay = Image.new('RGBA', (new_width, new_height), (255, 255, 255,0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(font_path, 22)
    font2 = ImageFont.truetype(font_path, 24)

    fv_differences = [0]
    # 初始化基准FV为最后一个元素的第一个玩家的FV值
    base_fv = json_data[-1]['Players'][0]['FV']
    # 从倒数第二个元素开始向前遍历json_data
    for i in range(len(json_data) - 2, -1, -1):
        # 当前元素的第一个玩家的FV值
        current_fv = json_data[i]['Players'][0]['FV']
        # 计算当前元素的FV与基准FV的差值
        fv_diff = current_fv - base_fv
        # 更新基准FV为当前元素的FV
        base_fv = current_fv
        # 将差值添加到fv_differences数组的开始位置
        fv_differences.insert(0, fv_diff)
    draw.rectangle((0, 0, new_width, new_height), fill=(255, 255, 255 ,150))
    
    for index,item in enumerate(json_data):
        UsedTime = max(int(item['UsedTime']) //60,1)
        CreateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(item['CreateTime'])))
        Player_Data = item['Players'][0]
        HeroID = int(Player_Data['HeroID'])
        if not (hero := await get_hero_name(HeroID)):
            hero = '未知英雄'
        HeroLv = int(Player_Data['HeroLv'])
        Result = Player_Data['Result']
        SummonerSkill1 = int(Player_Data['SummonerSkill1'])
        SummonerSkill2 = int(Player_Data['SummonerSkill2'])
        FV = int(Player_Data['FV'])
        Ep = Player_Data['Ep']
        KillPlayer = int(Player_Data['KillPlayer'])
        Death = int(Player_Data['Death'])
        Assist = int(Player_Data['Assist'])
        KillUnit = int(Player_Data['KillUnit'])
        hero_hurt = await num2k(int(Player_Data['MD'][-1]))
        hero_bear = await num2k(int(Player_Data['TD'][-1]))
        TotalMoney = int(Player_Data['TotalMoney'])
        MakeDamagePercent = "{:.2f}".format(Player_Data['MakeDamagePercent'] * 100).rstrip('0').rstrip('.')
        TotalMoneyPercent = "{:.2f}".format(Player_Data['TotalMoneyPercent'] * 100).rstrip('0').rstrip('.')
        DamageConversionRate = "{:.2f}".format(Player_Data['DamageConversionRate'] * 100).rstrip('0').rstrip('.')
        KDA = "{:.2f}".format((KillPlayer + Assist) / max(Death,1)).rstrip('0').rstrip('.')
        info_data = f'{KillPlayer}/{Death}/{Assist}/{KillUnit}'
        hurt_bear = f'伤:{hero_hurt} 承:{hero_bear}'

        # 行间距
        once_line_spacing = int(new_height//len(json_data))

        line_spacing = once_line_spacing*index
        result_line_spacing = once_line_spacing*(index+1)

        if Result == 1:
            draw.rectangle((0, line_spacing, 48, result_line_spacing), fill=(0, 255, 0,60))
        elif Result == 2:
            draw.rectangle((0, line_spacing, 48, result_line_spacing), fill=(255, 0, 0,60))
        _, text_height = draw.textsize(f'{HeroLv}', font=font)
        _, text2_height = draw.textsize(f'{HeroLv}', font=font2,stroke_width=2)
        font_up_line_spacing = once_line_spacing //2 - text_height
        font_down_line_spacing = once_line_spacing //2
        font2_line_spacing = (once_line_spacing - text2_height) // 2

        image_line_spacing = (once_line_spacing - 64) // 2

        draw.text((10, font2_line_spacing+line_spacing), f'{HeroLv}', fill=(255,255,255), font=font2,stroke_fill=(0, 0, 0),stroke_width=2)
        overlay = await draw_image_on_canvas(overlay, HeroID, (60, image_line_spacing+line_spacing), 'hero')

        draw.text((60, line_spacing), f'{CreateTime}', fill=(0, 0, 0), font=font)
        draw.text((150, font2_line_spacing+line_spacing), f'{hero}', fill=(0, 0, 0), font=font2)

        draw.text((295, line_spacing), f'用时:{UsedTime}分', fill=(0, 0, 0), font=font)
        draw.text((295, font2_line_spacing+line_spacing), f'分:{FV}', fill=(0, 0, 0), font=font2)
        diff = fv_differences[index]
        if diff >= 0:
            diff = f'+{diff}'
            diff_fill = (0, 255, 0)
            if diff == '+0':
                diff_fill = (0, 0, 0)
        else:
            diff_fill = (255, 0, 0)
        draw.text((380, font2_line_spacing+line_spacing), f'{diff}', fill=diff_fill, font=font2,stroke_width=1,stroke_fill=(0,0,0))

        overlay = await draw_image_on_canvas(overlay,SummonerSkill1,(440, image_line_spacing+line_spacing),'skill')
        overlay = await draw_image_on_canvas(overlay,SummonerSkill2,(505, image_line_spacing+line_spacing),'skill')

        for EP_index,EP_item in enumerate(Ep):
            # 单数跳过
            if EP_index % 2:
                continue
            if EP_item := int(EP_item):
                overlay = await draw_image_on_canvas(overlay,EP_item,(int(610 + EP_index / 2 * 65), image_line_spacing + line_spacing),'equipment')
        
        draw.text((1560, font2_line_spacing+line_spacing), f'评分:{KDA}', fill=(0, 0, 0), font=font2)

        draw.text((1050, font_up_line_spacing+line_spacing), info_data, fill=(0, 0, 0), font=font)
        draw.text((1050, font_down_line_spacing+line_spacing), hurt_bear, fill=(0, 0, 0), font=font)

        draw.text((1250, font_up_line_spacing+line_spacing), f'{TotalMoney}', fill=(0, 0, 0), font=font)
        draw.text((1250, font_down_line_spacing+line_spacing), f'{TotalMoneyPercent}%', fill=(0, 0, 0), font=font)

        draw.text((1360, font_up_line_spacing+line_spacing), f'伤害占比:{MakeDamagePercent}%', fill=(0, 0, 0), font=font)
        draw.text((1360, font_down_line_spacing+line_spacing), f'伤害转换:{DamageConversionRate}%', fill=(0, 0, 0), font=font)
        draw.line((0, result_line_spacing, new_width, result_line_spacing), fill=(0, 0, 0), width=1)
    img.paste(overlay, (0, 0), overlay)
    # img.show()
    return await image_to_base64(img)

async def draw_image_on_canvas(canvas, item_id, coordinates, item_type):
    """
    在给定的画布上绘制技能、装备或英雄图标。
    
    :param canvas: PIL Image对象，即绘图的画布。
    :param item_id: 要绘制的项目的ID（召唤师技能、装备、英雄ID）。
    :param coordinates: 在画布上粘贴图片的坐标（左上角）。
    :param item_type: 绘制类型，可为'skill'、'equipment'或'hero'。
    :return: 经过绘制后的画布（PIL Image对象）。
    """
    image_name = None

    try:
        if item_type == 'skill':
            image_name = f'ui/icon/skill/ico_{item_id}..dds'
        elif item_type == 'equipment':
            if not (equip_image := await get_equip_path(item_id)):
                return canvas
            image_name = os.path.splitext(equip_image)[0]
        elif item_type == 'hero':
            if not (hero_image := await get_hero_head(item_id)):
                return canvas
            image_name = f'{os.path.splitext(hero_image)[0]}.dds'.lower()
        else:
            raise ValueError(f"Unsupported item type: {item_type}")
        
        if image_name:
            image_path = os.path.join(image_dir, image_name)
            if not os.path.exists(image_path):
                return canvas

            item_img = Image.open(image_path).convert("RGBA")
            
            if item_type == 'hero':
                # 对英雄图标进行特殊处理：等比缩放和圆形裁剪
                target_size = 64
                item_img.thumbnail((target_size, target_size), Image.LANCZOS)
                mask = Image.new('L', (item_img.width, item_img.height), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, item_img.width, item_img.height), fill=255)
                result_img = Image.new("RGBA", (item_img.width, item_img.height), (255, 255, 255, 0))
                result_img.paste(item_img, (0, 0), mask)
                canvas.paste(result_img, coordinates, result_img.split()[3])
            else:
                canvas.paste(item_img, coordinates, item_img)
    except Exception as e:
        traceback.print_exc()
        print(f"Error drawing {item_type}: {e}")

    return canvas