from flask import Flask, render_template, request, jsonify
from src.douyin_comment import DouyinCommentGenerator
from src.history import HistoryManager
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

# 初始化历史记录管理器
history_manager = HistoryManager(app)

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

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/api/generate', methods=['POST'])
@limiter.limit("10 per minute")  # 每分钟最多10次请求
def generate():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'Please provide video URL'}), 400

        # 获取生成器实例
        try:
            gen = get_generator()
        except Exception as e:
            return jsonify({'error': 'API initialization failed: {0}'.format(str(e))}), 500

        # 下载视频信息并生成评论
        video_info = gen.download_video(url)
        if not video_info:
            return jsonify({'error': 'Failed to get video info, please check the URL'}), 400

        comment = gen.generate_comment(video_info['title'])
        if not comment:
            return jsonify({'error': 'Failed to generate comment, please try again later'}), 500

        # 保存历史记录
        history_manager.add_record(
            url, 
            video_info['title'], 
            comment,
            video_info.get('thumbnail_url')
        )

        return jsonify({
            'success': True,
            'title': video_info['title'],
            'thumbnail_url': video_info.get('thumbnail_url'),
            'comment': comment
        })

    except Exception as e:
        return jsonify({'error': 'Server error: {0}'.format(str(e))}), 500

@app.route('/api/history')
def get_history():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 限制每页数量，防止请求过大
        per_page = min(per_page, 50)
        
        records = history_manager.get_records(page=page, per_page=per_page)
        return jsonify({
            'success': True,
            **records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 添加错误处理
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'details': 'Please wait for a minute. {0}'.format(str(e.description))
    }), 429

# Vercel需要这个
app.debug = False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
