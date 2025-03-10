# BiliDownloader
一个简单的 B 站视频爬取下载器。项目编写于 2023 年，现已过时，仅供参考。

## 如何运行
项目使用标准 pyproject.toml 管理依赖。可通过 uv 等管理器安装依赖。
```bash
uv install --requirements pyproject.toml
```
本项目依赖于 FFmpeg 进行视频下载和处理，请在 `config.py` 中配置 FFmpeg 的路径。

安装依赖并配置 FFmpeg 后，使用 Python 运行 `BiliDownloader.py` 即可。
```bash
uv run BiliDownloader.py
```