import os
import yt_dlp
import requests
import json
import time
import re

class DouyinCommentGenerator:
    def __init__(self):
        # yt-dlp配置 - 只提取信息，不下载
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'no_write_playlist_metafiles': True,
            'writeinfojson': False,
            'writedescription': False,
            'writethumbnail': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'allsubtitles': False,
            'ignoreerrors': True,
            'clean_infojson': False,
            'format': 'best'
        }
        
        # 初始化文心一言API配置
        self.api_key = os.getenv('ERNIE_API_KEY')
        self.secret_key = os.getenv('ERNIE_SECRET_KEY')
        if not self.api_key or not self.secret_key:
            raise ValueError("请在.env文件中设置ERNIE_API_KEY和ERNIE_SECRET_KEY")
        
        # 获取access token
        self.access_token = self._get_access_token()
        if not self.access_token:
            raise ValueError("获取access token失败")

    def _get_access_token(self):
        """获取百度API access token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        try:
            response = requests.post(url, params=params)
            result = response.json()
            return result.get("access_token")
        except Exception as e:
            print(f"获取access token时出错: {e}")
            return None

    def _call_ernie_api(self, messages):
        """调用文心一言API"""
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={self.access_token}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "messages": messages
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            if "error_code" in result:
                print(f"API调用错误: {result}")
                return None
            return result.get("result", "")
        except Exception as e:
            print(f"API调用出错: {e}")
            return None

    def _convert_url(self, url):
        """转换抖音链接格式"""
        # 如果是发现页面链接，提取视频ID
        discover_match = re.search(r'modal_id=(\d+)', url)
        if discover_match:
            video_id = discover_match.group(1)
            return f"https://www.douyin.com/video/{video_id}"
        return url

    def download_video(self, url):
        """获取抖音视频信息（不实际下载）"""
        try:
            # 转换URL格式
            converted_url = self._convert_url(url)
            print("正在获取视频信息...")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    # 先尝试只获取基本信息
                    basic_info = ydl.extract_info(converted_url, download=False, process=False)
                    if basic_info and 'title' in basic_info:
                        return basic_info['title']
                    
                    # 如果获取基本信息失败，尝试获取完整信息
                    info = ydl.extract_info(converted_url, download=False)
                    return info.get('title', None)
                except Exception as e:
                    print(f"提取视频信息时出错: {str(e)}")
                    return None
        except Exception as e:
            print(f"获取视频信息时出错: {e}")
            return None

    def generate_comment(self, video_title):
        """使用文心一言生成评论文案"""
        max_retries = 3
        retry_delay = 5  # 重试等待时间（秒）
        
        for attempt in range(max_retries):
            try:
                messages = [
                    {
                        "role": "user",
                        "content": f"""请为这个抖音视频生成一个精辟的评论。
视频标题：{video_title}
要求：
1. 评论要简短有力（30字以内）
2. 要有趣、吸引人
3. 符合抖音风格和氛围
4. 能引起共鸣和互动
请直接给出评论内容，不要加任何额外的解释。"""
                    }
                ]
                
                result = self._call_ernie_api(messages)
                if result:
                    return result.strip()
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return None
