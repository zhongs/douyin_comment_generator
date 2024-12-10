import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class HistoryManager:
    def __init__(self, app=None):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
            
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        if app:
            self.init_app(app)

    def init_app(self, app):
        """初始化数据库连接"""
        # 确保表已创建
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """创建历史记录表（如果不存在）"""
        # Supabase 会自动创建表，这里我们可以运行一个检查查询
        try:
            self.supabase.table('history').select("id").limit(1).execute()
        except Exception as e:
            # 如果表不存在，创建它
            self.supabase.postgrest.rpc('create_history_table').execute()

    def add_record(self, video_url, video_title, comment, thumbnail_url=None):
        """添加一条历史记录"""
        data = {
            'video_url': video_url,
            'video_title': video_title,
            'comment': comment,
            'thumbnail_url': thumbnail_url,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table('history').insert(data).execute()
        return result.data

    def get_records(self, page=1, per_page=10):
        """获取历史记录，支持分页"""
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 获取总记录数
        count_result = self.supabase.table('history').select('id', count='exact').execute()
        total_count = count_result.count if hasattr(count_result, 'count') else 0
        
        # 获取分页数据
        result = self.supabase.table('history')\
            .select('*')\
            .order('created_at', desc=True)\
            .range(offset, offset + per_page - 1)\
            .execute()
            
        return {
            'records': result.data,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
