from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import subprocess
import threading
import hashlib
from urllib.parse import urlparse, parse_qs
from datetime import datetime

FRIEND_FILE = '/path/to/your/config/friend.json'
STANDALONE_FILE = '/path/to/your/.next/standalone/config/friend.json'
SETTINGS_FILE = '/path/to/your/down/settings.json'
POSTS_PATH = '/path/to/your/posts'
DOC_CONSTANTS_FILE = '/path/to/your/constants/doc.ts'
API_SECRET_FILE = '/path/to/your/down/api_secret.txt'

def read_friends():
    try:
        with open(FRIEND_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('friends', [])
    except Exception as e:
        print(f"Error reading friends: {e}")
        return []

def write_friends(friends):
    try:
        data = {'friends': friends}
        with open(FRIEND_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(STANDALONE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing friends: {e}")
        return False

def read_settings():
    try:
        if not os.path.exists(SETTINGS_FILE):
            return {
                's3Domain': '',
                'defaultAvatar': '/your-path/user/avatar/user_1/avatar.avif',
                'defaultAuthor': ''
            }
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading settings: {e}")
        return {
            's3Domain': '',
            'defaultAvatar': '/your-path/user/avatar/user_1/avatar.avif',
            'defaultAuthor': ''
        }

def write_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing settings: {e}")
        return False

def get_api_secret():
    try:
        if not os.path.exists(API_SECRET_FILE):
            secret = hashlib.sha256(os.urandom(32)).hexdigest()
            with open(API_SECRET_FILE, 'w') as f:
                f.write(secret)
            return secret
        else:
            with open(API_SECRET_FILE, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error getting API secret: {e}")
        return None

def verify_auth(auth_header):
    if not auth_header:
        return False
    
    try:
        auth_type, credentials = auth_header.split(' ', 1)
        if auth_type.lower() != 'bearer':
            return False
        
        token = credentials.strip()
        secret = get_api_secret()
        
        if not secret:
            return False
        
        return token == secret
    except Exception as e:
        print(f"Error verifying auth: {e}")
        return False

def read_categories():
    try:
        if not os.path.exists(DOC_CONSTANTS_FILE):
            return []
        
        with open(DOC_CONSTANTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        categories = []
        import re
        order = 0
        for line in content.split('\n'):
            if ':' in line and "'" in line and not line.strip().startswith('//'):
                match = re.match(r'\s*(\w+)\s*:\s*\'([^\']+)\'', line)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if key and value:
                        categories.append({'name': key, 'label': value, 'order': order})
                        order += 1
        
        return categories
    except Exception as e:
        print(f"Error reading categories: {e}")
        return []

def write_categories(categories):
    try:
        sorted_cats = sorted(categories, key=lambda x: x.get('order', 999))
        lines = ["export const docDirectoryLabelMap: Record<string, string> = {"]
        for cat in sorted_cats:
            lines.append(f"  {cat['name']}: '{cat['label']}',")
        lines.append("} as const")
        
        with open(DOC_CONSTANTS_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    except Exception as e:
        print(f"Error writing categories: {e}")
        return False

def get_category_post_count(category_name):
    try:
        category_path = os.path.join(POSTS_PATH, category_name)
        if not os.path.exists(category_path):
            return 0
        
        count = 0
        for file in os.listdir(category_path):
            if file.endswith('.mdx'):
                count += 1
        
        return count
    except Exception as e:
        print(f"Error counting posts: {e}")
        return 0

def read_posts(category=None):
    try:
        posts = []
        
        if category:
            category_path = os.path.join(POSTS_PATH, category)
            if not os.path.exists(category_path):
                return posts
            
            files = os.listdir(category_path)
            for file in files:
                if file.endswith('.mdx'):
                    post = read_post_file(os.path.join(category_path, file))
                    if post:
                        post['category'] = category
                        posts.append(post)
        else:
            for cat_dir in os.listdir(POSTS_PATH):
                cat_path = os.path.join(POSTS_PATH, cat_dir)
                if os.path.isdir(cat_path):
                    for file in os.listdir(cat_path):
                        if file.endswith('.mdx'):
                            post = read_post_file(os.path.join(cat_path, file))
                            if post:
                                post['category'] = cat_dir
                                posts.append(post)
        
        # 按置顶状态和日期排序：置顶优先，然后按日期降序
        posts.sort(key=lambda x: (x['pin'], x['date']), reverse=True)
        return posts
    except Exception as e:
        print(f"Error reading posts: {e}")
        return []

def read_post_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = {}
        body_content = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                body_content = parts[2]
                
                for line in frontmatter_str.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip("'").strip('"')
                        frontmatter[key] = value
        
        slug = os.path.basename(file_path).replace('.mdx', '')
        
        return {
            'slug': slug,
            'title': frontmatter.get('title', ''),
            'banner': frontmatter.get('banner', ''),
            'description': frontmatter.get('description', ''),
            'date': frontmatter.get('date', ''),
            'content': body_content.strip(),
            'authorName': frontmatter.get('authorName', 'Sora.'),
            'authorAvatar': frontmatter.get('authorAvatar', ''),
            'authorHomepage': frontmatter.get('authorHomepage', ''),
            'pin': frontmatter.get('pin', 'false') == 'true'
        }
    except Exception as e:
        print(f"Error reading post file: {e}")
        return None

def write_post(post, category, slug=None):
    try:
        import re
        settings = read_settings()
        
        if not slug:
            slug = post.get('title', '').lower().replace(' ', '-')
            slug = re.sub(r'[^\w-]', '', slug)
        
        category_path = os.path.join(POSTS_PATH, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        file_path = os.path.join(category_path, f'{slug}.mdx')
        
        frontmatter = [
            f"---",
            f"title: '{post.get('title', '')}'",
            f"banner: '{post.get('banner', '')}'",
            f"description: '{post.get('description', '')}'",
            f"date: {post.get('date', datetime.now().strftime('%Y-%m-%d'))}",
            f"authorUid: 1",
            f"authorName: '{settings.get('defaultAuthor', 'Sora.')}'",
            f"authorAvatar: '{settings.get('s3Domain', '')}{settings.get('defaultAvatar', '')}'",
            f"authorHomepage: 'https://www.arnebiae.com'",
            f"pin: false",
            f"---",
            "",
            post.get('content', '')
        ]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(frontmatter))
        
        return True
    except Exception as e:
        print(f"Error writing post: {e}")
        return False

def delete_post(category, slug):
    try:
        file_path = os.path.join(POSTS_PATH, category, f'{slug}.mdx')
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting post: {e}")
        return False

build_lock = threading.Lock()
build_status = {
    'building': False,
    'success': None,
    'message': '',
    'timestamp': None
}

def check_resources():
    try:
        import shutil
        disk = shutil.disk_usage('/14t_1/kun-touchgal-next')
        if disk.free < 5 * 1024 * 1024 * 1024:  # 至少5GB
            return False, '磁盘空间不足，至少需要5GB'
        return True, '资源检查通过'
    except Exception as e:
        return False, f'资源检查失败: {e}'

def build_and_restart():
    try:
        build_status['building'] = True
        build_status['success'] = None
        build_status['message'] = '正在构建...'
        build_status['timestamp'] = datetime.now().isoformat()
        
        resource_ok, resource_msg = check_resources()
        if not resource_ok:
            build_status['building'] = False
            build_status['success'] = False
            build_status['message'] = resource_msg
            return False
        
        os.chdir('/14t_1/kun-touchgal-next')
        
        build_log = []
        result = subprocess.run(
            ['pnpm', 'run', 'build'],
            capture_output=True,
            text=True,
            timeout=600
        )
        build_log.append(result.stdout)
        build_log.append(result.stderr)
        
        if result.returncode != 0:
            build_status['building'] = False
            build_status['success'] = False
            build_status['message'] = '构建失败: ' + (result.stderr or '未知错误')
            return False
        
        result = subprocess.run(['pm2', 'restart', 'kun-touchgal-next'], capture_output=True, text=True)
        build_log.append(result.stdout)
        build_log.append(result.stderr)
        
        build_status['building'] = False
        build_status['success'] = True
        build_status['message'] = '构建成功并已重启服务'
        return True
    except subprocess.TimeoutExpired:
        build_status['building'] = False
        build_status['success'] = False
        build_status['message'] = '构建超时（10分钟）'
        return False
    except Exception as e:
        build_status['building'] = False
        build_status['success'] = False
        build_status['message'] = f'构建错误: {e}'
        return False

class APIHandler(BaseHTTPRequestHandler):
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_json_response(200, {})
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        if not verify_auth(self.headers.get('Authorization')):
            self.send_json_response(401, {'success': False, 'message': 'Unauthorized'})
            return
        
        if path == '/api/rebuild-status':
            self.send_json_response(200, {'success': True, 'data': build_status})
        elif path == '/api/friends':
            friends = read_friends()
            self.send_json_response(200, {'success': True, 'data': friends})
        elif path == '/api/settings':
            settings = read_settings()
            self.send_json_response(200, {'success': True, 'data': settings})
        elif path == '/api/categories':
            categories = read_categories()
            for cat in categories:
                cat['postCount'] = get_category_post_count(cat['name'])
            self.send_json_response(200, {'success': True, 'data': categories})
        elif path == '/api/posts':
            category = query.get('category', [None])[0]
            posts = read_posts(category)
            self.send_json_response(200, {'success': True, 'data': posts})
        else:
            self.send_json_response(404, {'success': False, 'message': 'Not found'})
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            password = data.get('password', '')
            
            if password == 'admin123':
                secret = get_api_secret()
                self.send_json_response(200, {'success': True, 'token': secret})
            else:
                self.send_json_response(401, {'success': False, 'message': '密码错误'})
            return
        
        if not verify_auth(self.headers.get('Authorization')):
            self.send_json_response(401, {'success': False, 'message': 'Unauthorized'})
            return
        
        if path == '/api/friends':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            friends = data.get('friends', [])
            
            if write_friends(friends):
                self.send_json_response(200, {'success': True, 'message': '保存成功'})
            else:
                self.send_json_response(500, {'success': False, 'message': '保存失败'})
        elif path == '/api/settings':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if write_settings(data):
                self.send_json_response(200, {'success': True, 'message': '设置保存成功'})
            else:
                self.send_json_response(500, {'success': False, 'message': '保存失败'})
        elif path == '/api/categories':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            categories = read_categories()
            categories.append({
                'order': data.get('order', 0),
                'name': data.get('name'),
                'label': data.get('label')
            })
            
            if write_categories(categories):
                self.send_json_response(200, {'success': True, 'message': '栏目添加成功'})
            else:
                self.send_json_response(500, {'success': False, 'message': '保存失败'})
        elif path == '/api/posts':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if write_post(data, data.get('category')):
                self.send_json_response(200, {'success': True, 'message': '文章添加成功'})
            else:
                self.send_json_response(500, {'success': False, 'message': '保存失败'})
        elif path == '/api/rebuild':
            if build_status['building']:
                self.send_json_response(400, {'success': False, 'message': '构建正在进行中，请稍候'})
                return
            
            if not build_lock.acquire(blocking=False):
                self.send_json_response(400, {'success': False, 'message': '构建正在进行中，请稍候'})
                return
            
            try:
                self.send_json_response(200, {'success': True, 'message': '构建已启动，请稍候...'})
                thread = threading.Thread(target=build_and_restart)
                thread.start()
            finally:
                build_lock.release()
        else:
            self.send_json_response(404, {'success': False, 'message': 'Not found'})
    
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if not verify_auth(self.headers.get('Authorization')):
            self.send_json_response(401, {'success': False, 'message': 'Unauthorized'})
            return
        
        if path.startswith('/api/categories/'):
            category_name = path.split('/')[-1]
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            categories = read_categories()
            found = False
            for cat in categories:
                if cat['name'] == category_name:
                    cat['name'] = data.get('name', category_name)
                    cat['label'] = data.get('label', cat['label'])
                    cat['order'] = data.get('order', cat.get('order', 0))
                    found = True
                    break
            
            if found and write_categories(categories):
                self.send_json_response(200, {'success': True, 'message': '栏目更新成功'})
            else:
                self.send_json_response(404, {'success': False, 'message': '栏目不存在'})
        elif path.startswith('/api/posts/'):
            slug = path.split('/')[-1]
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if write_post(data, data.get('category'), slug):
                self.send_json_response(200, {'success': True, 'message': '文章更新成功'})
            else:
                self.send_json_response(500, {'success': False, 'message': '保存失败'})
        else:
            self.send_json_response(404, {'success': False, 'message': 'Not found'})
    
    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if not verify_auth(self.headers.get('Authorization')):
            self.send_json_response(401, {'success': False, 'message': 'Unauthorized'})
            return
        
        if path.startswith('/api/categories/'):
            category_name = path.split('/')[-1]
            categories = read_categories()
            categories = [cat for cat in categories if cat['name'] != category_name]
            
            if write_categories(categories):
                self.send_json_response(200, {'success': True, 'message': '栏目删除成功'})
            else:
                self.send_json_response(500, {'success': False, 'message': '删除失败'})
        elif path.startswith('/api/posts/'):
            parts = path.split('/')
            if len(parts) >= 4:
                category = parts[-2]
                slug = parts[-1]
                
                if delete_post(category, slug):
                    self.send_json_response(200, {'success': True, 'message': '文章删除成功'})
                else:
                    self.send_json_response(404, {'success': False, 'message': '文章不存在'})
            else:
                self.send_json_response(400, {'success': False, 'message': 'Invalid request'})
        else:
            self.send_json_response(404, {'success': False, 'message': 'Not found'})
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8082), APIHandler)
    print('Friend API Server running on port 8082')
    server.serve_forever()
