# 300英雄战绩查询(Hoshino插件)

[![Lisence](https://img.shields.io/github/license/Himeno-Yumemi/300hero_record)]((LICENSE))
![PythonVer](https://img.shields.io/badge/python-3.8+-blue)
[![HoshinoVer](https://img.shields.io/badge/Hoshino-v2.0.0%2B-green)](https://github.com/Ice-Cirno/HoshinoBot)

> __重要更新__
> 
> 2024年1月9日 首次上传
>
> 2024年2月19日 修复绑定失败等错误,优化jjc详情(目前可以查询他人的对局详情),设置最大显示局数为8局
> 
> 2024年2月27日 图片功能测试
## 简介

用于群里开庭群友,某些人经济吃完不干事,必须拷打

## 功能：

> - 获取指定玩家的近`max_page`(最大为8)场竞技场或战场的核心数据
> - 在群中以图片的形式发送,防止文本刷屏(图片版还在锐意制作中)
> - 支持指令绑定玩家名，可以使用@进行对应玩家的查询。
> - 图片版本的各功能(测试中)
> - ~~协议、业务分离设计，方便不同机器人平台进行移植~~ （模块分离了,指令还没改）


## 部署

本人是windows系统,linux没试过

1. 进入到Hoshino的modules目录，克隆项目

`git clone https://github.com/Himeno-Yumemi/300hero_record.git`

2. 安装依赖的包

`pip install -r ./requirements.txt ` (还没做,PIL只能小于10.0.0,我用的9.5.0)


3. 将'config/config_example.json'重命名为 config.json

<details>

<summary>config配置详情</summary>

<code>

    "json_url":{
            "equip_jjc":"https://300data.com/data/api/item_jjc_list", # jjc装备更新api
            "equip_zc":"https://300data.com/data/api/item_zc_list", # zc装备更新api
            "hero": "https://300data.com/data/api/banner_hero_ex_list"  # 英雄数据更新api
        },
    "COOKIES":{
        "PHPSESSID": "",    # 数据更新api的cookies(必须填)
        "RECORD_COOKIES":"" # 官方战报查询网的cookies(必须填)
    },
    "record_url":{
        "rolename":"https://300report.jumpw.com/api/battle/searchNormal?type=h5",   # 玩家数据api
        "match_list":"https://300report.jumpw.com/api/battle/searchMatchs?type=h5", # 玩家对局列表api
        "match_info":"https://300report.jumpw.com/api/battle/searchMatchinfo?type=h5"   # 玩家对局详情api
    },
    "max_page": 8,   # 图片最大查询局数
    "image":{
        "enable": true,   # 是否启用图片功能
        "font_name":"SourceHanSansSC-Regular.otf"  # 字体名称
    }

</code>

> PHPSESSID: 访问https://300data.com/ 在cookies里复制值过来

> RECORD_COOKIES: 访问https://300report.jumpw.com/#/ 在F12控制台输入`console.log(document.cookie);`复制返回结果

</details>

4. 在`config/__bot__.py`的`MODULES_ON`中，添加`"300hero_record"`，然后重启HoshinoBot。

## 使用

> []:必填
>
> ():可填
>
> (测试名称)均能换成@XXXX进行他人的查询

### 1-绑定角色

群内发送  `绑定角色[测试名称]` 即可进行`测试名称`的绑定

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/1.png)

绑定之后的指令不需要(测试名称)就能进行查询,且可以使用@进行他人的查询

群内发送 `查看角色(@XXXX)` 可查看绑定角色信息,可@查看他人

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/2.png)

### 2-战绩查询

群内发送  `jjc(测试名称)` 即可获取最近`测试名称`的对局信息。

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/3.png)

### 3-战绩详情查询

群内发送 `jjc详情[1](测试名称)` 即可获取指定序号的对局详情数据。

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/4.png)

### 4-今日胜场查询

群内发送 `jjc胜场(测试名称)` 即可获取指定用户的今日胜场数据。

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/5.png)

### 5-数据更新

支持机器人管理员进行游戏数据的更新。

指令:`更新300英雄数据`

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/6.png)

### 6-图片功能

支持 `jjc`和`jjc详情` 两个指令

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/7.png)

![image](https://github.com/Himeno-Yumemi/300hero_record/blob/main/readme_image/8.png)

### 鸣谢

[Ice-Cirno/HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)

[300英雄资料站](https://x.300data.com)
