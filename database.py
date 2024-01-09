from tortoise.models import Model
from tortoise import fields
from tortoise import Tortoise
import os

#同路径下database文件夹下的路径
database_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'database')
database_path = os.path.join(database_dir, 'user.sqlite3')

class UserInfo(Model):
    id = fields.IntField(pk=True)
    uid = fields.IntField(index=True)
    gid = fields.IntField(index=True)
    name = fields.CharField(max_length=30)
    class Meta:
        table = 'user'

    #获取全部用户
    @classmethod
    async def get_all(cls):
        if user_list := await cls.all().values_list('uid','gid','name'):
            return user_list

    #获取用户信息
    @classmethod
    async def get_info(cls, uid:int,gid):
        if user := await cls.get_or_none(uid=uid,gid=gid):
            return user

    #删除用户
    @classmethod
    async def del_info(cls,uid:int,gid:int):
        if info := await cls.get_or_none(uid=uid,gid=gid):
            await info.delete()
            return True

    #修改任意数据
    @classmethod
    async def set_info(cls,uid:int,gid:int,**kwargs):
        if await cls.get_or_none(uid=uid,gid=gid):
            await cls.filter(uid=uid).update(**kwargs)
            return True

async def init():
    await Tortoise.init(
        db_url='sqlite:///'+database_path,
        modules={'models': [__name__]}
    )
    await Tortoise.generate_schemas()
#增
async def add_info(uid,gid,name):
    user_info = UserInfo(uid=uid,gid=gid,name=name)
    await user_info.save()