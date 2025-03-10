import pathlib

TITLE = "BiliDownloader"
ROOT_PATH = pathlib.Path(__file__).parent.absolute()
DATA_PATH = ROOT_PATH / "data"
RESOURCE_PATH = DATA_PATH / "resource"
FFMPEG_PATH = ROOT_PATH / "ffmpeg.exe"
RES_OPTIONS = ("超清 4K", "高清 1080P+", "高清 1080P", "高清 720P", "清晰 480P", "流畅 360P")
TIPS_STR = """Cookie获取方法：
打开浏览器，随后打开并登录https://www.bilibili.com/，然后点开任意一个视频。
接下来在视频所在页面中按F12呼出控制台, 在上方的菜单栏中选择“网络”（或"Network"）。
点开左侧菜单栏中任意一项，然后在右侧找到"Cookie:"项，
将其全部复制到本程序的修改Cookie界面中（如果没找到就在左侧菜单中换一个点开）
"""

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://www.bilibili.com",
    "Referer": "https://www.bilibili.com"
}
