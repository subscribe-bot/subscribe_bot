from typing import *
import random
import base64
import asyncio as ai
import enum

import regex as re
from objprint import op
# from async_property import async_cached_property
from sqlalchemy import Column, ForeignKey, Index, Enum, UniqueConstraint
from sqlalchemy import select
from sqlalchemy.types import Text, Integer, String, Boolean
from sqlalchemy.orm import relationship, backref, Query, WriteOnlyMapped, DeclarativeBase
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from .base import get_session, commit, flush, Base



class User(Base):
  """
  用户类, 用于存储用户的信息
  """
  __tablename__ = "users"
  __mapper_args__ = {"eager_defaults": True}  # required in order to access columns with server defaults or SQL expression defaults, subsequent to a flush, without triggering an expired load

  id = Column(Integer, primary_key=True)
  name = Column(String(32), unique=True, index=True)
  password = Column(String(32))

  w_platforms: WriteOnlyMapped['Platform'] = relationship(
      'Platform', back_populates='user', lazy='write_only')
  w_tasks: WriteOnlyMapped['CrawlTask'] = relationship(
      'CrawlTask',
      back_populates='w_users',
      lazy='write_only',
      secondary='send_message_tasks')
  
  async def refresh(self, what: Literal["all", "platforms", "tasks"] = "all"):
    sess=get_session()
    if what!="tasks":
      self.platforms=(await sess.scalars(self.w_platforms.select())).all()
    if what!="platforms":
      self.tasks=(await sess.scalars(self.w_tasks.select())).all()



  @staticmethod
  async def init_register(name: str, password: str) -> Union['User', None]:
    """注册, 返回注册的用户对象, 如果用户名重复则返回None"""
    user = User(name=name, password=password)

    sess=get_session()
    sess.add(user)

    if (await commit(catch_classes=IntegrityError, catch_regex=r"\(1062")):
      return user
    else: 
      return None
  
  @staticmethod
  async def init_login(name: str, password: str):
    """登录, 返回用户对象, 如果用户名或密码错误则返回None"""
    sess=get_session()
    user = await sess.scalar(
      select(User).filter(
        User.name == name, User.password == password))
    return user
  
  @staticmethod
  async def init_by_token(token: str)->Union['User', None]:
    """用于验证token, 如果验证通过则直接返回对应的user对象, 否则返回None"""
    sess=get_session()
    platform: Union[Platform, None] = await sess.scalar(
      select(Platform).filter_by(token=token))

    return getattr(platform, 'user', None)
  
  
  async def bind_platform(self, platform: 'Platform'):
    """绑定平台"""
    self.w_platforms.add(platform)
    return await flush(raise_exp=True)



class Platform(Base):
  """
  平台类, 用于存储用户绑定平台的信息
  可以生成token, 用于验证用户身份
  """
  class Type(enum.Enum):
    """平台类型"""
    qq = 'qq'
    WeChat = 'wechat'
  
  __tablename__ = "platforms"
  __mapper_args__ = {"eager_defaults": True}

  id = Column(Integer, primary_key=True)
  token = Column(String(20))
  username = Column(String(100), nullable=False)
  type = Column(Enum(Type), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'))

  user:User = relationship('User', back_populates='w_platforms', uselist=False, lazy='selectin')

  Index('platforms_index', 'username', 'type', unique=True)
  UniqueConstraint('user_id', 'type', name='bind_unique')


  @staticmethod
  async def init_register(username: str, type: Type) -> Union['Platform', None]:
    """根据用户名和平台名创建一个新platform, 如果发生重复则返回None"""
    ret=Platform(username=username, type=type)
    sess=get_session()
    sess.add(ret)
    if await commit(catch_classes=IntegrityError, catch_regex=r"\(1062"):
      return ret
    else: 
      return None


  @staticmethod
  async def generate_token(username:str, type:str):
    """检测username和type是否已经存在, 不存在则创建Platform与新User, 并返回20字节的token"""
    token=base64.b64encode(random.randbytes(15),b'-_').decode('utf-8')

    sess=get_session()
    platform: Union[Platform, None]= await sess.scalar(
      select(Platform).filter_by(username=username, type=type))

    if platform is None:
      user=User()
      sess.add(user)
      await sess.flush()
      platform = Platform(user_id=user.id, token=token, username=username, type=type)
      sess.add(platform)
    else:
      platform.token = token
    await commit()

    return token
  




class SendMessageTask(Base):
  """
  作为用户和爬取任务的中间表存在; 同时也保存着对应任务的发送对象
  任务的发送对象需要经过校验(由user类调用platform类完成), 以防止用户发送消息给不属于自己的账号
  """
  __tablename__ = "send_message_tasks"

  id = Column(Integer, primary_key=True)
  crawl_task_id = Column(Integer, ForeignKey('crawl_tasks.id'), index=True)
  user_id = Column(Integer, ForeignKey('users.id'), index=True)
  # platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False)
  message_title_template = Column(String(200))
  message_body_template = Column(Text)
  target_type = Column(Enum('qq_person', 'qq_group', 'wechat_person', 'wechat_group', 'mail'), nullable=False)
  target_username = Column(String(60), nullable=False)

  # platform:List[Platform] = relationship('Platform', uselist=False, lazy='selectin')
  # crawl_task:CrawlTask = relationship('CrawlTask', uselist=False, lazy='selectin')



class CrawlTask(Base):
  """
  爬取任务表, 保存了爬取任务的信息(描述, 爬取对象, 包的类型, 爬取频率等)
  """
  __tablename__ = "crawl_tasks"
  __mapper_args__ = {"eager_defaults": True}

  id = Column(Integer, primary_key=True)
  name = Column(String(32), index=True)
  description = Column(String(500))
  hided = Column(Boolean, default=True)

  url= Column(Text, nullable=False)
  url_hided = Column(Boolean)
  header = Column(Text)
  header_hided = Column(Boolean)
  cookie = Column(Text)
  cookie_hided = Column(Boolean)
  body = Column(String(2000))
  body_hided = Column(Boolean)
  code = Column(Text)
  code_hided = Column(Boolean)

  interval = Column(Integer, nullable=False)#multiples of 10 minutes
  last_message_hash = Column(String(128))
  next_crawl_task = Column(Integer, ForeignKey('crawl_tasks.id'))#next task to run after this one
  version = Column(Integer, default=0)#optimistic lock

  regex = Column(String(1000))

  regex_groups:List['RegexGroup'] = relationship('RegexGroup', cascade="all, delete-orphan", lazy='selectin')
  w_users:WriteOnlyMapped[User] = relationship('User', back_populates='w_tasks', lazy='write_only', secondary='send_message_tasks')
  send_message_tasks:List[SendMessageTask] = relationship('SendMessageTask', lazy='selectin', overlaps="w_tasks,w_users")#overlaps可能是一个更深的坑, 出问题先找它


  async def users(self):
    sess=get_session()
    return (await sess.scalars(self.w_users.select())).all()



class RegexGroup(Base):
  """
  用于正则匹配的对应, 保存了正则表达式的位置和对应的组名, 以及所属的爬取任务
  """
  __tablename__='regex_groups'

  id = Column(Integer, primary_key=True)
  index = Column(Integer, nullable=False)
  name = Column(String(32))
  task_id = Column(Integer, ForeignKey('crawl_tasks.id'), index=True, nullable=False)
