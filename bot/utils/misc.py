import copy
import inspect
import random
from typing import *


def kwargs_to_dict()->Dict[str,Any]:
  """Get the kwargs of the caller function. Must be called in first line."""
  kwargs=copy.copy(inspect.currentframe().f_back.f_locals)
  return kwargs


def get_random_str(length=10, mode:Literal["all", "digit", "lower", "upper", "letter", "word", "url"]="all"):
  """
  生成一个指定长度的随机字符串
  """
  dic={
    "digit":"""0123456789""",
    "lower":"""abcdefghijklmnopqrstuvwxyz""",
    "upper":"""ABCDEFGHIJKLMNOPQRSTUVWXYZ""",
    "letter":"""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ""",
    "word":"""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789""",
    "url":"""-_.!~*'()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789""",
    "all":"""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ """,
  }
  str_list =[random.choice(dic[mode]) for _ in range(length)]
  return ''.join(str_list)
