from os import fspath
import pathlib
import requests
import re
import json
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox as Messagebox
import tkinter.filedialog as Filedialog
from tkinter import scrolledtext
from PIL import Image, ImageTk
import ffmpy
import CookieOperation as cookieOP
from config import (
    ROOT_PATH,
    DATA_PATH,
    RESOURCE_PATH,
    TITLE,
    TIPS_STR,
    headers,
    RES_OPTIONS,
    FFMPEG_PATH,
)


COVER_W = 535
COVER_H = 100000  # 充分大


def resize(w: int, h: int, wBox: int, hBox: int, pilImg: Image) -> Image:
    f1 = 1.0 * wBox / w
    f2 = 1.0 * hBox / h
    factor = min([f1, f2])
    width = int(w * factor)
    height = int(h * factor)
    return pilImg.resize((width, height), Image.LANCZOS)


def mergeVideoAudio(
    videoPath: pathlib.Path,
    audioPath: pathlib.Path,
    outputPath: pathlib.Path,
    deleteAudio: bool = True,
) -> None:
    """
    合并音视频

    Args:
        videoPath (pathlib.Path): 视频文件路径
        audioPath (pathlib.Path): 音频文件路径
        outputPath (pathlib.Path): 输出的视频路径
        deleteAudio (bool): 是否删除音频, 默认为True

    Returns:
        None
    """
    videoFinal = ffmpy.FFmpeg(
        executable=fspath(FFMPEG_PATH),
        inputs={fspath(videoPath): None, fspath(audioPath): None},
        outputs={outputPath: "-c:v copy -c:a aac -strict experimental"},
    )
    videoFinal.run()
    if deleteAudio:
        audioPath.unlink()
    videoPath.unlink()


def copyFile(resource: pathlib.Path, target: pathlib.Path):
    r = resource.open(mode="rb")
    t = target.open(mode="wb")
    t.write(r.read())
    r.close()
    t.close()


class BiliDownloader(Frame):
    def __init__(self, master) -> None:
        # 定义变量
        self.videoCover = pathlib.Path()
        self.videoCover = RESOURCE_PATH / "defaultCover.jpg"
        self.bvcode = StringVar()
        self.videoTitle = StringVar()
        self.videoFileTitle = str
        self.videoAuthor = StringVar()
        self.videoPublishedDate = StringVar()
        self.videoUrl = StringVar()
        self.promptText = StringVar()
        self.videoPartsNum = int
        self.videoPartsNum = 1
        for i in [
            self.bvcode,
            self.videoTitle,
            self.videoAuthor,
            self.videoPublishedDate,
        ]:
            i.set("")
        self.master = master
        self.downloadPathText = StringVar()
        self.downloadPathText.set(fspath(ROOT_PATH / "output"))
        self.downloadPath = ROOT_PATH / "output"
        self.resOption = 6
        self.resOptionMax = 6  # 与config.py中的RES_OPTIONS顺序对应
        self.initDownloadPath()
        self.initWidgets()

    def initWidgets(self):
        # 创建左对齐风格
        self.styleLeftAligned = Style()
        self.styleLeftAligned.configure("leftAligned.TLabel", justify=LEFT, anchor=W)
        # 划分左右两个区域
        frameLeft = Frame(self.master)
        frameRight = Frame(self.master)
        frameLeft.grid(column=0, row=0, sticky=NSEW)
        frameRight.grid(column=1, row=0, sticky=NSEW)
        # *左半部分控件
        # 输入链接部分
        self.videoUrl.set("输入视频链接或BV号")
        urlEntry = Entry(frameLeft, text="视频链接", textvariable=self.videoUrl)
        urlEntry.grid(column=0, row=0, sticky=(EW))
        urlEntry.bind("<Return>", self.parse)
        parseButton = Button(
            frameLeft, text="解析", command=lambda: self.parse(self.videoUrl.get())
        )
        parseButton.grid(column=1, row=0)
        # 视频信息显示
        info = Labelframe(frameLeft, text="视频信息")
        info.grid(column=0, columnspan=2, row=1, sticky=(EW))
        bvcodeL = Label(info, text="BV号: ", style="leftAligned.TLabel")
        videoTitleL = Label(info, text="视频标题: ", style="leftAligned.TLabel")
        videoAuthorL = Label(info, text="视频作者: ", style="leftAligned.TLabel")
        videoPublishedDateL = Label(info, text="发布日期: ", style="leftAligned.TLabel")
        infosL = [bvcodeL, videoTitleL, videoAuthorL, videoPublishedDateL]
        for i, j in zip(infosL, range(0, len(infosL))):
            i.grid(column=0, row=j, sticky=W)
        bvcodeR = Label(info, textvariable=self.bvcode, style="leftAligned.TLabel")
        videoTitleR = Label(
            info, textvariable=self.videoTitle, style="leftAligned.TLabel"
        )
        videoAuthorR = Label(
            info, textvariable=self.videoAuthor, style="leftAligned.TLabel"
        )
        videoPublishedDateR = Label(
            info, textvariable=self.videoPublishedDate, style="leftAligned.TLabel"
        )
        infosR = [bvcodeR, videoTitleR, videoAuthorR, videoPublishedDateR]
        for i, j in zip(infosR, range(0, len(infosR))):
            i.grid(column=1, row=j, sticky=W)
        # 下载选项
        downloadOption = Labelframe(frameLeft, text="下载选项")
        downloadOption.grid(column=0, columnspan=3, row=2, sticky=(EW))
        Label(downloadOption, text="下载路径: ", style="leftAligned.TLabel").grid(
            column=0, row=0, columnspan=3, sticky=W
        )
        downloadPathEntry = Entry(downloadOption, textvariable=self.downloadPathText)
        downloadPathEntry.grid(column=0, row=1, columnspan=2, sticky=EW)
        downloadPathChangeButton = Button(
            downloadOption, text="选择下载路径", command=lambda: self.chooseDownloadPath("")
        )
        downloadPathChangeButton.grid(column=2, row=1, sticky=EW)
        changeCookieButton = Button(
            downloadOption, text="修改Cookies", command=self.changeCookie
        )
        changeCookieButton.grid(column=0, row=2, columnspan=3, sticky=EW)
        Label(downloadOption, text="下载清晰度: ").grid(column=0, row=3, sticky=W)
        chooseResStrVal = StringVar()
        self.chooseRes = Combobox(
            downloadOption,
            textvariable=chooseResStrVal,
            values=("(空)", *RES_OPTIONS[self.resOptionMax : 6]),
        )
        self.chooseRes.grid(column=1, row=3, columnspan=2, sticky=EW)
        chooseResStrVal.set("(空)")
        self.chooseRes.current(0)
        chooseFileStrVal = StringVar()
        chooseFile = Combobox(
            downloadOption,
            textvariable=chooseFileStrVal,
            values=("仅视频(不保留音频)", "仅音频", "音频和视频", "封面"),
        )
        chooseFile.grid(column=0, row=4, columnspan=2, sticky=EW)
        downloadButton = Button(
            downloadOption, text="下载", command=lambda: self.download(chooseFile)
        )
        downloadButton.grid(column=2, row=4)
        self.progress = Progressbar(
            frameLeft, orient=HORIZONTAL, length=200, mode="determinate"
        )
        self.progress.grid(column=0, columnspan=3, row=3, sticky=(EW))
        self.progressInfoText = StringVar()
        self.progressInfoText.set("下载进度将显示在上方。")
        progressInfo = Label(frameLeft, textvariable=self.progressInfoText)
        progressInfo.grid(column=0, columnspan=3, row=4, sticky=(EW))
        # *右半部分控件
        self.updateCover()
        videoCoverLabelFrame = Labelframe(frameRight, text="视频封面")
        videoCoverLabelFrame.grid(column=0, row=0, sticky=N)
        self.coverLabel = Label(videoCoverLabelFrame)
        self.coverLabel.configure(image=self.videoCoverImage)
        self.coverLabel.image = self.videoCover
        self.coverLabel.update()
        self.coverLabel.grid(sticky=NSEW)

    def download(self, downloadOptionCombobox: Combobox) -> None:
        choice = downloadOptionCombobox.get()
        if pathlib.Path(self.downloadPathText.get()) != self.downloadPath:
            self.chooseDownloadPath(self.downloadPathText.get())
        if choice == "封面":
            copyFile(
                resource=self.videoCover,
                target=self.downloadPath / (self.videoFileTitle + ".jpg"),
            )
        else:
            self.changeResOption(self.chooseRes)
            if choice == "仅视频(不保留音频)":
                self.getVideo()
            elif choice == "仅音频":
                self.getVideo(audioOnly=True)
            elif choice == "音频和视频":
                self.getVideo(keepAudio=True)
            else:
                Messagebox.showerror("ERROR", "错误的下载选项")

    def parse(self, url: str):
        # 检查链接有效性
        bvcodeMatch = re.search(r"BV\w{10}", url)
        if bvcodeMatch is None:
            Messagebox.showinfo("ERROR", "请检查输入的链接")
        else:
            self.bvcode.set(bvcodeMatch.group(0))
            self.getVideoInfos()
            self.getCookie()
            self.getVideoURL()

    def initDownloadPath(self):
        existFileResult = (ROOT_PATH / "config.json").is_file()
        if not existFileResult:
            configJSON = (ROOT_PATH / "config.json").open(mode="w")
            newDict = {
                "output": fspath(ROOT_PATH / "output"),
                "cookie": {"SESSDATA": ""},
            }
            json.dump(
                newDict, configJSON, sort_keys=True, indent=4, separators=(",", ":")
            )
            configJSON.close()
        else:
            try:
                configJSON = (ROOT_PATH / "config.json").open(mode="r")
                result = dict(json.load(configJSON))
                self.downloadPath = pathlib.Path(result["output"])
                self.downloadPathText.set(fspath(self.downloadPath))
            except json.decoder.JSONDecodeError:
                configJSON.close()
                configJSON = (ROOT_PATH / "config.json").open(mode="w")
                newDict = {
                    "output": fspath(ROOT_PATH / "output"),
                    "cookie": {"SESSDATA": ""},
                }
                json.dump(
                    newDict, configJSON, sort_keys=True, indent=4, separators=(",", ":")
                )
            except KeyError:
                configJSON.close()
                result.update({"output": fspath(ROOT_PATH / "output")})
                configJSON = (ROOT_PATH / "config.json").open(mode="w")
                json.dump(
                    result, configJSON, sort_keys=True, indent=4, separators=(",", ":")
                )
            finally:
                configJSON.close()

    def chooseDownloadPath(self, path: str):
        if path == "":  # 确认是下载按钮还是选择下载路径按钮触发函数
            pathName = Filedialog.askdirectory()
            if pathName != "":  # 如果用户选择路径
                self.downloadPath = pathlib.Path(pathName)
                self.downloadPathText.set(fspath(self.downloadPath))
                configJSON = (ROOT_PATH / "config.json").open(mode="r")
                result = dict(json.load(configJSON))
                configJSON.close()
                configJSON = (ROOT_PATH / "config.json").open(mode="w")
                result["output"] = self.downloadPathText.get()
                json.dump(
                    result, configJSON, sort_keys=True, indent=4, separators=(",", ":")
                )
                configJSON.close()
        else:
            self.downloadPath = pathlib.Path(self.downloadPathText.get())
            if self.downloadPath.is_dir():  # 检查路径是否存在
                configJSON = (ROOT_PATH / "config.json").open(mode="r")
                result = dict(json.load(configJSON))
                configJSON.close()
                configJSON = (ROOT_PATH / "config.json").open(mode="w")
                result["output"] = self.downloadPathText.get()
                json.dump(
                    result, configJSON, sort_keys=True, indent=4, separators=(",", ":")
                )
                configJSON.close()
                Messagebox.showinfo("提示", "下载路径已更改！")
            elif self.downloadPath.is_absolute():
                try:
                    self.downloadPath.mkdir(parents=True)
                    configJSON = (ROOT_PATH / "config.json").open(mode="r")
                    result = dict(json.load(configJSON))
                    configJSON.close()
                    configJSON = (ROOT_PATH / "config.json").open(mode="w")
                    result["output"] = fspath(self.downloadPath)
                    json.dump(
                        result,
                        configJSON,
                        sort_keys=True,
                        indent=4,
                        separators=(",", ":"),
                    )
                    configJSON.close()
                    Messagebox.showinfo("提示", "下载路径已创建并更改！")
                except FileNotFoundError:
                    Messagebox.showerror("ERROR", "请检查输入的路径")
            else:
                Messagebox.showerror("ERROR", "请检查输入的路径")

    def updateCover(self) -> None:
        videoCoverFile = Image.open(self.videoCover)
        w, h = videoCoverFile.size
        videoCoverFile = resize(w, h, COVER_W, COVER_H, videoCoverFile)
        self.videoCoverImage = ImageTk.PhotoImage(videoCoverFile)

    def getVideoInfos(self):
        htmlData = self.getPage(
            f"https://www.bilibili.com/video/{self.bvcode.get()}"
        ).text
        # 更新视频信息部分
        self.videoAuthor.set(
            re.search(
                r"name=\"author\" content=\"(.*)\"><meta data-vue-meta=\"true\" itemprop=\"name\" name=\"title\"",
                htmlData,
            ).group(1)
        )
        title = re.search(r"<h1 title=\"(.*?)\" class=\"video-title\"", htmlData).group(
            1
        )
        self.videoFileTitle = re.sub(r"|[\\/:*?\"<>|]+", "", title.strip())
        if len(title) > 17:
            title = title[0:15] + "..."
        self.videoTitle.set(title)
        self.videoPublishedDate.set(
            re.search(
                r"itemprop=\"datePublished\" content=\"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\"",
                htmlData,
            ).group(1)
        )
        # 更新封面部分
        videoCoverUrl = re.search(
            r"itemprop=\"image\" content=\"(.*?)@100w_100h_1c.png", htmlData
        ).group(1)
        if videoCoverUrl is not None:
            videoCoverUrl = "https:" + videoCoverUrl
            videoCover = requests.get(videoCoverUrl)
            (DATA_PATH / "temp").mkdir(exist_ok=True)
            tempVideoCoverPath = DATA_PATH / (
                "temp/tempCover." + videoCoverUrl.split(".")[-1]
            )
            self.videoCover = tempVideoCoverPath
            tempVideoCover = (tempVideoCoverPath).open(mode="wb")
            tempVideoCover.write(videoCover.content)
            tempVideoCover.close()
        else:
            self.videoCover = RESOURCE_PATH / "coverGetFailure.png"
        # 刷新界面中的封面图片
        self.updateCover()
        self.coverLabel.configure(image=self.videoCoverImage)
        self.coverLabel.update()
        self.master.update_idletasks()

    def getCookie(self):
        configJSON = (ROOT_PATH / "config.json").open(mode="r")
        result = dict(json.load(configJSON))
        self.biliCookie = dict(result["cookie"])
        configJSON.close()
        if self.biliCookie["SESSDATA"] == "":
            updateCookie = Messagebox.askokcancel(
                "提示",
                "当前Cookie为空，将无法获取480P以上清晰度的视频。\n\
                是否更新Cookie?",
            )
            if updateCookie:  # 跳出子窗口输入新Cookie
                self.changeCookie()

    def changeCookie(self):
        def updateCookieCommand():  # 保存新Cookie
            newCookie = cookieEntry.get("1.0", "end")
            newCookie = newCookie.replace("\n", "")
            if newCookie == "":
                newCookie = "SESSDATA=12345678;"  # 防报错
                Messagebox.showwarning(
                    "警告", '输入的cookie为空, 已重置为\n"{"SESSDATA": "12345678"}"'
                )
            newCookie = cookieOP.getCookieDict(newCookie)
            self.biliCookie = newCookie
            configJSON = (ROOT_PATH / "config.json").open(mode="r")
            result = dict(json.load(configJSON))
            configJSON.close()
            result["cookie"] = newCookie
            configJSON = (ROOT_PATH / "config.json").open(mode="w")
            json.dump(
                result, configJSON, sort_keys=True, indent=4, separators=(",", ":")
            )
            configJSON.close()
            updateCookieWindow.destroy()
            Messagebox.showinfo("提示", "Cookies保存成功！")

        def useTips():
            useTipsWindow = Toplevel(updateCookieWindow)
            useTipsWindow.title("Cookie使用提示")
            useTipsWindow.geometry("550x100")
            useTipsWindow.resizable(False, False)
            useTipsText = Label(useTipsWindow, state=DISABLED, text=TIPS_STR)
            useTipsText.place(relx=0.025, relheight=0.9, relwidth=0.95, rely=0.05)

        updateCookieWindow = Toplevel(self.master)
        updateCookieWindow.title("请输入Cookie")
        updateCookieWindow.geometry("400x300")
        updateCookieWindow.resizable(False, False)
        cookieEntry = scrolledtext.ScrolledText(updateCookieWindow)
        cookieEntry.place(relx=0.05, relheight=0.8, relwidth=0.9, rely=0.05)
        saveCookieButton = Button(
            updateCookieWindow, text="保存Cookie", command=updateCookieCommand
        )
        saveCookieButton.place(relx=0.35, relheight=0.1, relwidth=0.6, rely=0.875)
        useTipsButton = Button(updateCookieWindow, text="使用提示", command=useTips)
        useTipsButton.place(relx=0.05, relheight=0.1, relwidth=0.3, rely=0.875)

    def getPage(self, url: str, useCookie: bool = False) -> requests.Response:
        try:  # 获取html文件
            if useCookie:
                html = requests.get(url, headers=headers, cookies=self.biliCookie)
            else:
                html = requests.get(url, headers=headers)
            html.raise_for_status()
            html.encoding = html.apparent_encoding
        except requests.HTTPError:
            Messagebox.showerror("ERROR", f"解析失败，请检查网络情况(状态码: {html.status_code})")
        else:
            return html

    def getVideoURL(self):
        def getVideoMaxRes(k: int = 0) -> int:
            try:
                videoResMax = int(videoJSON["data"]["dash"]["video"][k]["id"])
                if videoResMax == 120:
                    videoResMax = 0  # 4K
                elif 120 > videoResMax > 80:
                    videoResMax = 1  # 1080P60
                elif videoResMax == 80:
                    videoResMax = 2  # 1080P30
                elif videoResMax == 64:
                    videoResMax = 3  # 720P
                elif videoResMax == 32:
                    videoResMax = 4  # 480P
                elif videoResMax == 16:
                    videoResMax = 5  # 360P
                else:
                    videoResMax = getVideoMaxRes(k + 1)
            except IndexError:
                Messagebox.showerror("ERROR", "未解析到正确的分辨率选项，请检查网络情况")
                return 0
            else:
                return videoResMax

        videoJSONText = re.findall(
            "<script>window.__playinfo__=(.*?)</script>",
            self.getPage(
                f"https://www.bilibili.com/video/{self.bvcode.get()}", useCookie=True
            ).text,
            re.S,
        )[0]
        videoJSON = json.loads(videoJSONText)
        videoJSONFile = (DATA_PATH / "temp" / "videoInfosTemp.json").open(mode="w")
        json.dump(
            videoJSON, videoJSONFile, sort_keys=True, indent=4, separators=(",", ":")
        )
        videoJSONFile.close()
        self.resOptionMax = getVideoMaxRes()
        self.chooseRes.configure(values=("(空)", *RES_OPTIONS[self.resOptionMax : 6]))

    def changeResOption(self, combobox: Combobox):
        choice = combobox.get()
        if choice == "(空)":
            self.resOption = 0
        elif choice == "超清 4K":
            self.resOption = 1
        elif choice == "高清 1080P+":
            self.resOption = 2
        elif choice == "高清 1080P":
            self.resOption = 3
        elif choice == "高清 720P":
            self.resOption = 4
        elif choice == "清晰 480P":
            self.resOption = 5
        elif choice == "流畅 360P":
            self.resOption = 6
        else:
            Messagebox.showerror("ERROR", "错误的清晰度选项！")

    def getVideo(self, audioOnly: bool = False, keepAudio: bool = False):
        def writeData(filename: str, response: requests.Response, path: pathlib.Path):
            totalSize = int(response.headers.get("content-length", 0))
            blockSize = 1024
            file = (path / filename).open(mode="wb")
            downloadSize = 0
            for data in response.iter_content(chunk_size=blockSize):
                file.write(data)
                downloadSize = downloadSize + len(data)
                self.progressInfoText.set(
                    f"下载中({int(downloadSize / 1024)}/{int(totalSize / 1024)} KB)"
                )
                self.updateProgressBar(progress=int(downloadSize / totalSize * 100))
            file.close()

        def downloadVideo():
            videoURL = videoJSON["data"]["dash"]["video"][resOption]["backup_url"][-1]
            response = requests.get(
                videoURL, headers=headers, cookies=self.biliCookie, stream=True
            )
            writeData(
                filename=self.videoFileTitle + ".mp4",
                response=response,
                path=self.downloadPath,
            )

        def downloadAudio():
            audioURL = videoJSON["data"]["dash"]["audio"][0]["backup_url"][-1]
            response = requests.get(
                audioURL, headers=headers, cookies=self.biliCookie, stream=True
            )
            writeData(
                filename=self.videoFileTitle + ".mp3",
                response=response,
                path=self.downloadPath,
            )

        videoJSONFile = (DATA_PATH / "temp" / "videoInfosTemp.json").open(mode="r")
        videoJSON = json.load(videoJSONFile)
        resOption = (self.resOption - self.resOptionMax - 1) * 3
        if resOption < 0:
            Messagebox.showerror("ERROR", "错误的清晰度选项！")
            return
        downloadAudio()
        if not audioOnly:
            downloadVideo()
            self.progressInfoText.set("正在合成音视频，请稍候")
            self.master.update()
            adlpath = self.downloadPath / (self.videoFileTitle + ".mp3")
            vdlpath = self.downloadPath / (self.videoFileTitle + ".mp4")
            mergeVideoAudio(
                audioPath=adlpath,
                videoPath=vdlpath,
                outputPath=(self.downloadPath / (self.videoFileTitle + "_Final.mp4")),
                deleteAudio=(not keepAudio),
            )
        self.progressInfoText.set("下载完成!")

    def updateProgressBar(self, progress: int):
        self.progress.configure(value=progress)
        self.master.update()


def onClosing(window: Tk, mainWindow: BiliDownloader):  # 测试用，关闭窗口事件触发
    window.destroy()


def windowInit(window: Tk, mainWindow: BiliDownloader):
    window.title(TITLE)
    window.geometry("800x327")
    window.minsize(800, 327)
    window.resizable(False, True)  # 禁止窗口横向缩放
    window.iconphoto(False, PhotoImage(file=fspath(RESOURCE_PATH / "icon.png")))
    window.protocol("WM_DELETE_WINDOW", lambda: onClosing(window, mainWindow))


root = Tk()
mainWindow = BiliDownloader(root)
windowInit(root, mainWindow)
root.mainloop()
