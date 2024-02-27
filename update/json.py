import httpx
import json
import os
import traceback
from ..config.config import get_config
from .headers import equip_headers, hero_headers
from ..core import hero_save_path, equip_save_path

url_config = get_config('json_url')
equip_jjc_url = url_config.get('equip_jjc', None)
equip_zc_url = url_config.get('equip_zc', None)

hero_url = url_config.get('hero', None)

async def fetch_data(url, headers, data=None):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
    except Exception:
        traceback.print_exc()
        return None

async def process_items(items):
    temp_list = {}
    for item in items:
        if item_url := item.get('itemimg', None):
            json_obj = {
                'item_url': item_url,
                'item_img': item_url.replace('https://img.300data.com/300data/res/', '')
            }
            if item_id := item.get('itemid', None):
                temp_list[item_id] = json_obj
    return temp_list

async def update_equip():
    data = {'page': 1, 'xpage': 1000, 'key': ''}
    jjc_dict,zc_dict = {},{}

    jjc_result = await fetch_data(equip_jjc_url, equip_headers, data)
    if jjc_result and 'list' in jjc_result:
       jjc_dict = await process_items(jjc_result['list'])

    zc_result = await fetch_data(equip_zc_url, equip_headers, data)
    if zc_result and 'list' in zc_result:
        zc_dict =await process_items(zc_result['list'])

    temp_list = {**jjc_dict, **zc_dict}

    with open(equip_save_path, 'w', encoding='utf-8') as f:
        json.dump(temp_list, f, ensure_ascii=False, indent=4)

    return True

async def hero_data(hero_result):
    items = json.loads(hero_result)
    temp_list = {}
    for item in items:
        hero_name = item.get('name', None)
        hero_img = item.get('head', None)
        json_obj = {
            'name': hero_name,
            'head': hero_img
        }
        if hero_id := item.get('id', None):
            temp_list[int(hero_id)] = json_obj
    return temp_list

async def update_hero():
    if hero_result := await fetch_data(hero_url, hero_headers):
        temp_list= await hero_data(hero_result)

        with open(hero_save_path, 'w', encoding='utf-8') as f:
            json.dump(temp_list, f, ensure_ascii=False, indent=4)
    return True