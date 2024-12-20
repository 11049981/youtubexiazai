from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import yt_dlp
import asyncio
import json
import os
import logging
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 设置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
# 将下载目录也挂载为静态目录
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
templates = Jinja2Templates(directory="templates")

# 创建下载目录
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# 存储下载任务状态
downloads = {}

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_video_info(url):
    with yt_dlp.YoutubeDL() as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info['title'],
                'duration': info['duration'],
                'author': info['uploader'],
                'description': info['description'],
                'thumbnail': info['thumbnail']
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

def clean_number_string(s):
    """清理包含ANSI转义序列的数字字符串"""
    if isinstance(s, (int, float)):
        return float(s)
    if not isinstance(s, str):
        return 0.0
    
    # 移除ANSI转义序列
    clean_s = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', s)
    clean_s = clean_s.strip()
    
    try:
        return float(clean_s)
    except (ValueError, TypeError):
        logger.warning(f"无法将字符串 '{s}' 转换为数字")
        return 0.0

async def download_video(url, video_id):
    download_path = DOWNLOAD_DIR / f"{video_id}.mp4"
    
    def progress_hook(d):
        try:
            if d['status'] == 'downloading':
                # 只使用最基本的进度计算
                downloaded = d.get('downloaded_bytes', 0)
                if not isinstance(downloaded, (int, float)):
                    downloaded = 0
                    
                total = d.get('total_bytes', 0)
                if not isinstance(total, (int, float)):
                    total = d.get('total_bytes_estimate', 0)
                if not isinstance(total, (int, float)):
                    total = 0
                
                if total > 0:
                    progress = min(100, int((downloaded / total) * 100))
                else:
                    progress = 0
                    
                downloads[video_id].update({
                    'progress': progress,
                    'downloaded_bytes': downloaded,
                    'total_bytes': total,
                    'status': 'downloading'
                })
                
            elif d['status'] == 'finished':
                downloads[video_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'file_path': str(download_path),
                    'file_size': os.path.getsize(download_path)
                })
                
        except Exception as e:
            logger.error(f"Progress calculation error: {str(e)}")
            downloads[video_id].update({
                'status': 'failed',
                'progress': 0,
                'error': str(e)
            })

    ydl_opts = {
        'format': 'best',
        'outtmpl': str(download_path),
        'progress_hooks': [progress_hook],
        'no_color': True,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'no_ansi': True,
        'progress_with_newline': False,
        'force_generic_extractor': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Starting download for video ID: {video_id}")
            ydl.download([url])
    except Exception as e:
        logger.error(f"Download failed for video ID {video_id}: {str(e)}")
        downloads[video_id].update({
            'status': 'failed',
            'error': str(e)
        })

def normalize_url(url):
    """标准化YouTube URL"""
    if 'youtu.be' in url:
        # 处理短链接
        video_id = url.split('/')[-1].split('?')[0]
        return f'https://www.youtube.com/watch?v={video_id}'
    return url

@app.get("/")
async def home(request: Request):
    videos = []
    for video_id, info in downloads.items():
        if info['status'] == 'completed':
            videos.append(info)
    return templates.TemplateResponse("index.html", {"request": request, "videos": videos})

@app.post("/download")
async def start_download(request: Request):
    data = await request.json()
    url = data.get('url')
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # 标准化URL
    url = normalize_url(url)
    
    # 获取视频信息
    video_info = get_video_info(url)
    video_id = str(len(downloads))
    
    downloads[video_id] = {
        'id': video_id,
        'url': url,
        'status': 'downloading',
        'progress': 0,
        **video_info
    }

    # 启动异步下载
    asyncio.create_task(download_video(url, video_id))
    return JSONResponse({'video_id': video_id})

@app.get("/progress/{video_id}")
async def get_progress(video_id: str):
    if video_id not in downloads:
        raise HTTPException(status_code=404, detail="Download not found")
    return downloads[video_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 