"""
将Cookie字符串转成字典
来自https://github.com/jiumeng714/bilibili_video_crawing/blob/main/CookieOperation.py
"""
import re


def getCookieDict(cookieStr: str):
    cookieStr = cookieStr.replace('\n', '')
    # 下面将过滤 cookie字符串，找出里面的 核心 SESSDATA
    result = re.search('SESSDATA([\w\W])*;', cookieStr).group()  # 由于是贪婪模式，还要过滤
    newCookieDict = result.split(';')[0]   # 确保只保留 SESSDATA
    # 转字典
    sessionData = newCookieDict.split('=')
    cookieName = sessionData[0]
    cookieVal = sessionData[1]

    return {str(cookieName): cookieVal}


def getCookieNewStr(cookieStr: str):
    cookieStr = cookieStr.replace('\n', '')
    # 下面进行将字符串转字典操作
    cookieStrLst = str.split(cookieStr, ';')
    newCookie = ''
    for param in cookieStrLst:
        params = str.split(param, '=')
        name = params[0].strip()
        value = params[1].strip()
        newCookie += name + '=' + value + '; '
    newCookie = newCookie.rstrip(';')
    return newCookie
