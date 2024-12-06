from flask import Flask, render_template, request, jsonify
from douyin_comment import DouyinCommentGenerator
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 创建限流器
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# 延迟初始化 DouyinCommentGenerator
generator = None

def get_generator():
    global generator
    if generator is None:
        generator = DouyinCommentGenerator()
    return generator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@limiter.limit("10 per minute")  # 每分钟最多10次请求
def generate():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': '请提供视频链接'}), 400

        # 获取生成器实例
        try:
            gen = get_generator()
        except Exception as e:
            return jsonify({'error': f'API初始化失败: {str(e)}'}), 500

        # 下载视频并生成评论
        video_title = gen.download_video(url)
        if not video_title:
            return jsonify({'error': '视频下载失败，请检查链接是否正确'}), 400

        comment = gen.generate_comment(video_title)
        if not comment:
            return jsonify({'error': '评论生成失败，请稍后再试'}), 500

        return jsonify({
            'success': True,
            'title': video_title,
            'comment': comment
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加错误处理
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': '请求太频繁，请稍后再试',
        'details': f'请等待一分钟后再试。{str(e.description)}'
    }), 429

# Vercel需要这个
app.debug = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
