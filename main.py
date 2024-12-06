import os
from pathlib import Path
import yt_dlp
import requests
import json
import time
import re

class DouyinCommentGenerator:
    def __init__(self):
        self.download_path = Path("downloads")
        self.download_path.mkdir(exist_ok=True)
        
        # yt-dlp配置
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
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
        print("API验证成功！")

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
        """下载抖音视频"""
        try:
            # 转换URL格式
            converted_url = self._convert_url(url)
            print(f"处理视频链接: {converted_url}")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(converted_url, download=True)
                return info.get('title', None)
        except Exception as e:
            print(f"下载视频时出错: {e}")
            if "Unsupported URL" in str(e):
                print("提示：请使用以下格式的链接：")
                print("1. 分享链接：https://v.douyin.com/xxx")
                print("2. 视频链接：https://www.douyin.com/video/xxx")
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
                    print(f"\n评论生成失败，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                    
            except Exception as e:
                print(f"生成评论时出错: {e}")
                if attempt < max_retries - 1:
                    print(f"\n遇到错误，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return None

def main():
    try:
        generator = DouyinCommentGenerator()
        
        while True:
            url = input("\n请输入抖音视频链接（输入'q'退出）: ")
            if url.lower() == 'q':
                break
                
            print("\n开始处理...")
            # 下载视频
            video_title = generator.download_video(url)
            if not video_title:
                print("视频下载失败，请检查链接是否正确")
                continue
                
            # 生成评论
            comment = generator.generate_comment(video_title)
            if comment:
                print("\n生成的评论：")
                print("-" * 50)
                print(comment)
                print("-" * 50)
            else:
                print("评论生成失败，请稍后再试")
    except Exception as e:
        print(f"\n程序出错: {e}")
        print("如果是API相关错误，请检查API密钥是否正确")

if __name__ == "__main__":
    main()
