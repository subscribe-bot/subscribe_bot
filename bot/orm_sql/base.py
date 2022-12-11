import traceback
from contextvars import ContextVar
from typing import *

import regex as re
from configparser import ConfigParser
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from ..config import config_ini_path
from ..utils import kwargs_to_dict


async_scoped_session = ContextVar('async_scoped_session', default=None)

# sync_engine = create_engine('mysql+pymysql://localhost:3306/subscribe_bot?user=root&password=pyyyyyy', echo=True, future=True)
# sync_Base = declarative_base()
# SessionMaker=sessionmaker(bind=engine)

cfg=ConfigParser()
cfg.read(config_ini_path)
engine=create_async_engine(
  "mysql+aiomysql://{host}:{port}/{database}?user={user}&password={password}".format(**cfg['mysql']),
  echo=False, future=True
)
SessionMaker=async_sessionmaker(bind=engine, class_=AsyncSession, future=True, expire_on_commit=False)



def get_session(**kwargs) -> AsyncSession:
  """获取单个协程的session"""
  if (sess:=async_scoped_session.get()) is None:
    sess=SessionMaker(**kwargs)
    async_scoped_session.set(sess)  # type: ignore
  assert isinstance(sess, AsyncSession), f'async_scoped_session.get() returned {type(sess)} but not AsyncSession'
  print(id(sess))
  return sess

def close_session():
  sess=async_scoped_session.get()
  if sess is not None:
    sess.close()
    async_scoped_session.set(None)

async def catch_exp(coroutine: Coroutine[Any, Any, None],
                    echo=False,
                    raise_exp=False,
                    catch_classes=Exception,
                    catch_regex=".*"):
  if not isinstance(catch_classes, tuple):
    catch_classes = (catch_classes, )


  try:
    await coroutine
    return True
  except catch_classes as e:
    if raise_exp:
      raise

    if catch_regex != ".*":
      info = str(e)
      if not re.search(catch_regex, info):
        raise

    if echo:
      traceback.print_exc()

    return False


async def commit(echo=False,
                 raise_exp=False,
                 catch_classes=Exception,
                 catch_regex=".*"):
  """
  当echo为True时才会打印错误信息
  当raise_exp为True时抛出错误
  当捕捉到的错误不符合catch_*参数时抛出错误
  如果有捕捉到错误, 就返回False, 否则返回True
  """
  kwargs=kwargs_to_dict()
  # async with get_session() as sess:
  sess=get_session()
  return await catch_exp(sess.commit(), **kwargs)
  

async def flush(echo=False,
                raise_exp=False,
                catch_classes=Exception,
                catch_regex=".*"):
  """
  当echo为True时才会打印错误信息
  当raise_exp为True时抛出错误
  当捕捉到的错误不符合catch_*参数时抛出错误
  如果有捕捉到错误, 就返回False, 否则返回True
  """
  kwargs=kwargs_to_dict()
  # async with get_session() as sess:
  sess=get_session()
  return await catch_exp(sess.flush(), **kwargs)



class Base(DeclarativeBase):
  """创建基类, 并且允许不对应的注解"""
  __allow_unmapped__ = True
