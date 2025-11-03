"""
获取局域网IP地址的完整解决方案
包含 Flask 后端服务和前端页面
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import socket
import netifaces
import json

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def get_local_ips():
    """
    获取所有网络接口的IP地址
    """
    ip_list = []
    
    try:
        # 方法1: 使用 netifaces 库获取所有网络接口
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            
            # 获取IPv4地址
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip and ip != '127.0.0.1':
                        ip_list.append({
                            'ip': ip,
                            'type': 'IPv4',
                            'interface': interface,
                            'category': categorize_ip(ip)
                        })
            
            # 获取IPv6地址
            if netifaces.AF_INET6 in addrs:
                for addr in addrs[netifaces.AF_INET6]:
                    ip = addr['addr'].split('%')[0]  # 移除接口标识符
                    if ip and not ip.startswith('fe80'):  # 过滤掉链路本地地址
                        ip_list.append({
                            'ip': ip,
                            'type': 'IPv6',
                            'interface': interface,
                            'category': 'IPv6'
                        })
    except Exception as e:
        print(f"netifaces method failed: {e}")
    
    # 方法2: 使用 socket 库作为备选方案
    if not ip_list:
        try:
            # 获取主机名
            hostname = socket.gethostname()
            # 获取所有IP地址
            for info in socket.getaddrinfo(hostname, None):
                ip = info[4][0]
                if ':' in ip:  # IPv6
                    if not ip.startswith('fe80'):
                        ip_list.append({
                            'ip': ip,
                            'type': 'IPv6',
                            'interface': 'unknown',
                            'category': 'IPv6'
                        })
                else:  # IPv4
                    if ip != '127.0.0.1':
                        ip_list.append({
                            'ip': ip,
                            'type': 'IPv4',
                            'interface': 'unknown',
                            'category': categorize_ip(ip)
                        })
        except Exception as e:
            print(f"socket method failed: {e}")
    
    # 方法3: 通过连接外部地址获取默认路由的本地IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # 确保这个IP不重复
        if not any(item['ip'] == local_ip for item in ip_list):
            ip_list.append({
                'ip': local_ip,
                'type': 'IPv4',
                'interface': 'default',
                'category': categorize_ip(local_ip)
            })
    except Exception as e:
        print(f"default route method failed: {e}")
    
    return ip_list

def categorize_ip(ip):
    """
    判断IP地址类型
    """
    if ip.startswith('192.168.'):
        return '局域网 (家庭网络)'
    elif ip.startswith('10.'):
        return '局域网 (企业网络)'
    elif ip.startswith('172.'):
        second_octet = int(ip.split('.')[1])
        if 16 <= second_octet <= 31:
            return '局域网 (企业网络)'
    elif ip.startswith('127.'):
        return '本地回环'
    
    return '公网地址'

def get_client_ip():
    """
    获取客户端的真实IP地址
    """
    # 尝试从各种请求头中获取真实IP
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

@app.route('/')
def index():
    """
    返回前端页面
    """
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get-server-ips', methods=['GET'])
def get_server_ips():
    """
    获取服务器端的局域网IP地址
    """
    try:
        ips = get_local_ips()
        return jsonify({
            'success': True,
            'server_ips': ips,
            'count': len(ips)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-client-info', methods=['GET'])
def get_client_info():
    """
    获取客户端信息（客户端通过此接口可以看到服务器看到的客户端IP）
    """
    try:
        client_ip = get_client_ip()
        return jsonify({
            'success': True,
            'client_ip': client_ip,
            'headers': dict(request.headers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 前端HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>局域网IP地址检测（前后端结合）</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            font-weight: 500;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .ip-list {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .ip-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }
        
        .ip-item:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .ip-item:last-child {
            margin-bottom: 0;
        }
        
        .ip-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .ip-address {
            font-family: 'Courier New', monospace;
            font-size: 18px;
            color: #333;
            font-weight: 600;
        }
        
        .ip-badge {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .ip-badge.lan {
            background: #4caf50;
        }
        
        .ip-badge.public {
            background: #ff9800;
        }
        
        .ip-badge.local {
            background: #9e9e9e;
        }
        
        .ip-details {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 14px;
            color: #1565c0;
        }
        
        .method-badge {
            display: inline-block;
            background: #764ba2;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .empty-state {
            text-align: center;
            padding: 30px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🌐 局域网IP地址检测</h1>
            <p class="subtitle">前后端结合方案 - 更准确地获取局域网IP地址</p>
            
            <div>
                <button class="btn" onclick="getServerIPs()">获取服务器局域网IP</button>
                <button class="btn" onclick="getClientInfo()">查看客户端IP</button>
                <button class="btn" onclick="getAllInfo()">获取所有信息</button>
            </div>
        </div>
        
        <div class="card" id="serverCard" style="display: none;">
            <h2>
                🖥️ 服务器局域网IP地址
                <span class="method-badge">后端获取</span>
            </h2>
            <div id="serverIPs"></div>
        </div>
        
        <div class="card" id="clientCard" style="display: none;">
            <h2>
                💻 客户端信息
                <span class="method-badge">服务器视角</span>
            </h2>
            <div id="clientInfo"></div>
        </div>
    </div>

    <script>
        async function getServerIPs() {
            const serverCard = document.getElementById('serverCard');
            const serverIPs = document.getElementById('serverIPs');
            
            serverCard.style.display = 'block';
            serverIPs.innerHTML = '<div class="loading"><div class="spinner"></div>正在获取服务器IP...</div>';
            
            try {
                const response = await fetch('/api/get-server-ips');
                const data = await response.json();
                
                if (data.success && data.server_ips.length > 0) {
                    let html = '<div class="ip-list">';
                    data.server_ips.forEach(item => {
                        const badgeClass = item.category.includes('局域网') ? 'lan' : 
                                         item.category.includes('公网') ? 'public' : 'local';
                        html += `
                            <div class="ip-item">
                                <div class="ip-header">
                                    <span class="ip-address">${item.ip}</span>
                                    <span class="ip-badge ${badgeClass}">${item.category}</span>
                                </div>
                                <div class="ip-details">
                                    接口: ${item.interface} | 类型: ${item.type}
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    html += `<div class="info-box">✅ 成功检测到 ${data.count} 个IP地址</div>`;
                    serverIPs.innerHTML = html;
                } else {
                    serverIPs.innerHTML = '<div class="empty-state">未检测到IP地址</div>';
                }
            } catch (error) {
                serverIPs.innerHTML = `<div class="empty-state">❌ 获取失败: ${error.message}</div>`;
            }
        }
        
        async function getClientInfo() {
            const clientCard = document.getElementById('clientCard');
            const clientInfo = document.getElementById('clientInfo');
            
            clientCard.style.display = 'block';
            clientInfo.innerHTML = '<div class="loading"><div class="spinner"></div>正在获取客户端信息...</div>';
            
            try {
                const response = await fetch('/api/get-client-info');
                const data = await response.json();
                
                if (data.success) {
                    let html = '<div class="ip-list">';
                    html += `
                        <div class="ip-item">
                            <div class="ip-header">
                                <span class="ip-address">${data.client_ip}</span>
                                <span class="ip-badge">客户端IP</span>
                            </div>
                            <div class="ip-details">
                                这是服务器看到的您的IP地址
                            </div>
                        </div>
                    `;
                    html += '</div>';
                    html += `<div class="info-box">
                        <strong>💡 说明：</strong><br>
                        • 如果客户端和服务器在同一局域网，会显示局域网IP（如 192.168.x.x）<br>
                        • 如果通过公网访问，会显示公网IP或代理IP
                    </div>`;
                    clientInfo.innerHTML = html;
                } else {
                    clientInfo.innerHTML = '<div class="empty-state">获取失败</div>';
                }
            } catch (error) {
                clientInfo.innerHTML = `<div class="empty-state">❌ 获取失败: ${error.message}</div>`;
            }
        }
        
        async function getAllInfo() {
            await getServerIPs();
            await getClientInfo();
        }
        
        // 页面加载时自动获取所有信息
        window.addEventListener('load', () => {
            setTimeout(getAllInfo, 500);
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("局域网IP地址检测服务")
    print("=" * 60)
    
    # 显示服务器的局域网IP
    local_ips = get_local_ips()
    print("\n服务器局域网IP地址:")
    for ip_info in local_ips:
        if '局域网' in ip_info['category']:
            print(f"  ✅ {ip_info['ip']} ({ip_info['category']})")
    
    print("\n访问地址:")
    for ip_info in local_ips:
        if '局域网' in ip_info['category']:
            print(f"  http://{ip_info['ip']}:5000")
    print("  http://localhost:5000")
    print("\n" + "=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)