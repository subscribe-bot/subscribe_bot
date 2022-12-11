from typing import *
import asyncio as ai
import pytest

import pytest_asyncio
from objprint import op

from bot.orm_sql import engine, Base
from bot.orm_sql import get_session, commit
from bot.orm_sql import User, Platform, SendMessageTask, CrawlTask
from bot.utils import get_random_str

aimark=pytest.mark.asyncio
aifix=pytest_asyncio.fixture
rd=get_random_str

UNIT_TIME=1

# def ai_run(func):
#   def ret(*args, **kwargs):
#     ai.get_event_loop().run_until_complete(func(*args, **kwargs))
#   return ret

@pytest.fixture(scope="session", autouse=True)
def event_loop():
  policy = ai.get_event_loop_policy()
  loop = policy.new_event_loop()
  yield loop
  loop.close()

@aifix(scope='session', autouse=True)
async def setup_module():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)
  await engine.dispose() #不加会报错, 可能是因为数据不会被刷到磁盘
  yield

# @aifix(scope='function')
# async def sess():
#   async with get_session() as sess:
#     yield sess



class TestUser:
  @aimark
  async def test_init_register_success(self):
    """注册新用户"""
    async with get_session() as sess:
      user=await User.init_register("pyy", "qwq")
      assert user is not None
      # op(user)
      assert user.id is not None

  @aimark
  async def test_init_register_failed(self):
    """注册已存在的用户"""
    async with get_session() as sess:
      user=await User.init_register("pyy", "hello")
      assert user is None

  @aimark
  async def test_bind_platform_success(self):
    """绑定一个平台账号"""
    async with get_session() as sess:
      u = await User.init_register(rd(), rd())
      assert u is not None
      
      p=await Platform.init_register(rd(), Platform.Type.qq)
      assert p is not None
      
      await u.bind_platform(p)
      await u.refresh("platforms")
      assert u.platforms[0] is p
      await commit()



class TestPlatform:
  @aimark
  async def test_generate_token(self):
    token=await Platform.generate_token("1234567890", "qq")
    assert await User.init_by_token(token) is not None

  # @aimark
  # async def test_
