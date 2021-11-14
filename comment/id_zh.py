# -*- coding: utf8 -*-
"""
微博ID互转工具
"""
str62keys = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def trans_10id(id_str):
    """62进制id转换为10进制mid"""
    ret = ''
    while len(id_str) > 0:
        part_str = id_str[-4:]
        id_str = id_str[:-4]
        ten_part = to_ten(part_str)
        ret = ten_part + ret
    return ret


def to_ten(s):
    """62进制转换为10进制"""
    k = 1
    ten_ret = 0
    for i in s[::-1]:
        x = str62keys.index(i) * k
        ten_ret += x
        k *= 62
    str_ret = str(ten_ret)
    if len(s) == 4:
        str_ret = str_ret.rjust(7, '0')
    return str_ret


def trans_62id(mid):
    u"""10进制id转换为62进制id"""
    mid = str(mid)
    str_62 = ''
    while len(mid) > 0:
        mid_part = mid[-7:]
        mid = mid[:-7]
        part_62 = ten_to_62(mid_part)
        str_62 = part_62 + str_62
    return str_62


def ten_to_62(number):
    num = int(number)
    ret_62 = ''
    while num > 0:
        num, sur = divmod(num, 62)
        ret_62 = str62keys[sur] + ret_62
    if len(number) == 7:
        ret_62 = ret_62.rjust(4, '0')
    return ret_62

# 数字 —> 英文
# print trans_62id('4298322590306434')
# print trans_10id('GF5QAlCKW')
