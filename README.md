# Admin Server & Friend API

这是一个针对 [kun-touchgal-next](https://github.com/KUN1007/kun-touchgal-next) 项目的站外管理器，提供了友情链接和文章的管理功能。

## 项目说明

[kun-touchgal-next](https://github.com/KUN1007/kun-touchgal-next) 项目本身的后台没有友情链接和文章的管理功能，本项目作为一个独立的站外管理器，补充了这些功能。

**注意：** 本项目需要在部署了 kun-touchgal-next 程序之后才能使用。

## 目录结构

```
down/
├── admin.html          # 后台管理界面
├── admin_server.py      # 后台服务器（8081端口）
├── friend_api.py        # API服务器（8082端口）
├── index.html           # 维护页
├── settings.json        # 系统配置
├── favicon.ico          # 网站图标（需要替换为你自己的图标）
├── api_secret.txt       # API密钥（需要创建）
└── README.md            # 本文件
```

## 配置说明

### 1. admin_server.py（维护站配置）

**需要修改的配置：**

**第4行：修改为你的维护站实际路径**
```python
ADMIN_DIR = '/path/to/your/down'
```
将`/path/to/your/down`修改为你的维护站实际路径，例如：`/home/user/admin`

**说明：** 此路径指向维护站文件所在的目录，包含index.html、admin.html、settings.json等文件。

**第114行：修改端口号（如果需要）**
```python
server = HTTPServer(('0.0.0.0', 8081), CustomHandler)
```
将`8081`修改为你想要的端口号

**第114行：修改打印信息中的服务器地址**
```python
print('Admin Server running on http://your-domain-or-ip:8081/')
```
将`your-domain-or-ip`修改为你的实际IP地址或域名

### 2. friend_api.py（API站配置 + touchgal源站配置）

**需要修改的配置：**

**第10-15行：修改API站和touchgal源站路径**

**API站配置（维护站）：**
```python
SETTINGS_FILE = '/path/to/your/down/settings.json'
API_SECRET_FILE = '/path/to/your/down/api_secret.txt'
```
将`/path/to/your/down`修改为你的维护站实际路径

**touchgal源站配置：**
```python
FRIEND_FILE = '/path/to/your/config/friend.json'
STANDALONE_FILE = '/path/to/your/.next/standalone/config/friend.json'
POSTS_PATH = '/path/to/your/posts'
DOC_CONSTANTS_FILE = '/path/to/your/constants/doc.ts'
```
将`/path/to/your`修改为你的touchgal源站实际路径

**说明：** 
- API站配置指向维护站文件
- touchgal源站配置指向kun-touchgal-next项目文件
- API站会读取和修改touchgal源站的文件

**第43-47行：修改默认配置（如果settings.json不存在）**
```python
's3Domain': 'http://your-s3-domain.com:9000',
'defaultAvatar': 'http://your-s3-domain.com/your-path/user/avatar/user_1/avatar.avif',
'defaultAuthor': 'Your Name'
```
修改为你的S3域名、默认头像路径和默认作者名

**第52-56行：修改默认配置（如果读取settings.json失败）**
```python
's3Domain': 'http://your-s3-domain.com:9000',
'defaultAvatar': 'http://your-s3-domain.com/your-path/user/avatar/user_1/avatar.avif',
'defaultAuthor': 'Your Name'
```
修改为你的S3域名、默认头像路径和默认作者名

**第403行：修改默认登录密码**
```python
if password == 'your-default-password':
```
将`your-default-password`修改为你自己的强密码

**第615行：修改端口号（如果需要）**
```python
server = HTTPServer(('0.0.0.0', 8082), RequestHandler)
```
将`8082`修改为你想要的端口号

### 3. settings.json（维护站配置）

**需要修改的配置：**

```json
{
  "s3Domain": "",
  "defaultAvatar": "/your-path/user/avatar/user_1/avatar.avif",
  "defaultAuthor": ""
}
```

**配置说明：**
- `s3Domain`: 填写你的S3存储服务域名（可选，留空则不使用S3存储）
  - 例如：`http://your-s3-domain.com:9000`
- `defaultAvatar`: 填写默认头像的相对路径（可选，留空则不设置默认头像）
  - 例如：`/your-path/user/avatar/user_1/avatar.avif`
  - 将`your-path`替换为你的实际路径
  - 系统会自动将`s3Domain + defaultAvatar`组合成完整的头像URL
- `defaultAuthor`: 填写你的默认作者名（可选，留空则不设置默认作者）

**说明：** 此配置文件用于维护站，存储S3域名、默认头像和默认作者等系统设置。所有配置项都是可选的，根据需要填写即可。头像URL会自动由`s3Domain`和`defaultAvatar`组合生成。

### 4. api_secret.txt

创建并设置API密钥：

```bash
echo "your-secret-key" > api_secret.txt
```

**重要：** 请使用强密码，不要使用默认密钥。

### 5. 修改登录密码

默认登录密码为`SB111111`，请修改为强密码。

**修改方法：**

编辑`friend_api.py`文件，找到第403行：

```python
if password == 'SB111111':  # 修改这里的密码
```

将`SB111111`修改为你自己的强密码。

**建议：** 使用至少12位的复杂密码，包含大小写字母、数字和特殊字符。

### 6. 修改网站名称

默认网站名称为`SoraGal`，请修改为你自己的网站名称。

**修改方法：**

1. **修改admin.html**：
   - 第6行：修改标题
   - 第269行：修改页面标题

2. **修改index.html**：
   - 第6行：修改标题
   - 第127行：修改页面标题
   - 第171行：修改标题
   - 第183行：修改标题

3. **修改settings.json**：
   - 第3行：修改默认头像路径中的`your-path`为你的路径

4. **修改friend_api.py**：
   - 第44行和第53行：修改默认头像路径中的`your-path`为你的路径

5. **修改admin.html中的JavaScript**：
   - 第1005行：修改头像路径中的`your-path`为你的路径
   - 第1415行：修改头像路径中的`your-path`为你的路径

**示例：**

将所有`your-path`替换为你的网站名称或路径，例如：
- `mywebsite`
- `blog`
- `your-site-name`

### 7. 修改链接地址

**修改index.html中的链接：**

**第150-151行：修改按钮链接**
```html
<a href="https://your-website.com" class="btn" target="_blank" id="nav-btn">🌐 Navigation</a>
<a href="https://your-qq-group-link.com" class="btn" target="_blank" id="qq-btn">💬 QQ Group</a>
```
将`https://your-website.com`修改为你的网站链接
将`https://your-qq-group-link.com`修改为你的QQ群链接

**修改admin.html中的链接：**

**第464行：修改作者主页链接**
```html
<input type="url" class="form-input" id="post-author-homepage" placeholder="请输入作者主页链接" value="https://your-website.com">
```
将`https://your-website.com`修改为你的作者主页链接

**第1010行：修改作者主页默认值**
```javascript
document.getElementById('post-author-homepage').value = 'https://your-website.com';
```
将`https://your-website.com`修改为你的作者主页链接

**第1056行：修改作者主页默认值**
```javascript
document.getElementById('post-author-homepage').value = editingPost.authorHomepage || 'https://your-website.com';
```
将`https://your-website.com`修改为你的作者主页链接

**第1105行：修改作者主页默认值**
```javascript
authorHomepage: authorHomepage || 'https://your-website.com',
```
将`https://your-website.com`修改为你的作者主页链接

### 9. 设置网站图标

**说明：**

本项目默认提供了一个网站图标`favicon.ico`，你需要将其替换为你自己的网站图标。

**设置方法：**

1. **准备你的网站图标**：
   - 格式：`.ico`格式
   - 尺寸：建议使用32x32或16x16像素
   - 文件名：必须命名为`favicon.ico`

2. **替换图标文件**：
   - 将你的`favicon.ico`文件替换项目中的`favicon.ico`文件
   - 确保文件名完全一致（包括大小写）

3. **图标访问**：
   - 图标会自动在浏览器标签页显示
   - 访问地址：`http://your-domain-or-ip:8081/favicon.ico`

**注意事项：**

- 图标文件必须命名为`favicon.ico`，不能修改文件名
- 图标文件必须放在项目根目录下
- 替换后可能需要清除浏览器缓存才能看到新图标
- 如果图标不显示，请检查文件名和路径是否正确

**图标制作工具推荐：**

- [Favicon.io](https://favicon.io/) - 在线生成favicon
- [Canva](https://www.canva.com/) - 在线设计工具
- [GIMP](https://www.gimp.org/) - 免费图像编辑软件

### 10. 修改文本内容

你可以根据自己的需求修改HTML文件中的所有文本内容。

**index.html中的文本内容：**

- 网站标题和副标题
- 维护状态提示
- 系统更新说明
- 温馨提示
- 按钮文本
- 链接地址

**admin.html中的文本内容：**

- 后台管理标题
- 菜单项名称
- 表单标签
- 按钮文本
- 提示信息
- 错误信息

**修改方法：**

直接编辑HTML文件，找到需要修改的文本内容进行替换即可。

**示例：**

将"Galgame Sharing Heaven!"修改为你的宣传标语
将"友链管理"修改为其他菜单项名称
将"🌐 Navigation"修改为其他按钮文本

## 安装和运行

### 1. 系统要求

- Python 3.x
- 已部署 [kun-touchgal-next](https://github.com/KUN1007/kun-touchgal-next) 项目

### 2. 依赖库

本项目只使用Python标准库，无需安装任何第三方依赖：

- `http.server` - HTTP服务器
- `json` - JSON数据处理
- `os` - 文件系统操作
- `subprocess` - 子进程管理
- `threading` - 多线程支持
- `hashlib` - 哈希算法
- `urllib.parse` - URL解析
- `datetime` - 日期时间处理
- `re` - 正则表达式
- `shutil` - 文件操作工具

### 3. 安装依赖

```bash
# 无需安装额外依赖，只需要Python 3.x
python3 --version
```

### 4. 创建API密钥

```bash
echo "your-secret-key" > api_secret.txt
```

### 5. 启动服务器

```bash
# 启动API服务器（8082端口）
python3 friend_api.py &

# 启动后台服务器（8081端口）
python3 admin_server.py &
```

### 6. 访问

- 维护页: `http://your-domain-or-ip:8081/`
- 后台管理: `http://your-domain-or-ip:8081/admin/`
- API接口: `http://your-domain-or-ip:8081/api/`

## 功能说明

### 后台服务器（8081端口）

- `/` - 维护页
- `/admin/` - 后台管理界面
- `/favicon.ico` - 网站图标
- `/api/*` - API转发到8082端口
- 其他路径 - 返回404

### API服务器（8082端口）

提供以下API接口：

- `/api/friends` - 友链管理
- `/api/posts` - 文章管理
- `/api/categories` - 分类管理
- `/api/settings` - 系统设置
- `/api/build` - 构建和重启

## 安全建议

1. **修改默认端口**：建议修改默认端口号
2. **使用强密码**：API密钥必须使用强密码
3. **防火墙设置**：只开放必要的端口
4. **定期备份**：定期备份配置和数据
5. **访问控制**：建议使用反向代理（如Nginx）进行访问控制

## 故障排除

### 端口被占用

```bash
# 检查端口占用
lsof -i :8081
lsof -i :8082

# 杀死占用端口的进程
kill -9 <PID>
```

### 权限问题

```bash
# 修改文件权限
chmod 644 *.html *.py *.json
chmod 600 api_secret.txt
```

### 文件路径错误

确保所有路径配置正确，可以使用绝对路径或相对路径。

## 贡献

欢迎提交Issue和Pull Request！

## 作者信息

- **作者**: Sora.
- **QQ**: 2338795574
- **交流1群**: 792782974
- **交流2群**: 1075791960

## 许可证

MIT License
