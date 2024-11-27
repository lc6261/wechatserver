from flask import Flask, request, jsonify
import jwt
import time
import requests

app = Flask(__name__)

# 微信小程序的 AppID 和 AppSecret
APP_ID = 'YOUR_APP_ID'
APP_SECRET = 'YOUR_APP_SECRET'

# 生成 JWT 的密钥
JWT_SECRET_KEY = 'your_jwt_secret_key'

@app.route('/login', methods=['POST'])
def login():
    # 获取前端发送的 code
    data = request.get_json()
    code = data.get('code')

    if not code:
        return jsonify({'success': False, 'message': '缺少 code 参数'}), 400

    # 向微信服务器请求获取 openId 和 sessionKey
    response = requests.get(
        f'https://api.weixin.qq.com/sns/jscode2session',
        params={
            'appid': APP_ID,
            'secret': APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
    )

    if response.status_code != 200:
        return jsonify({'success': False, 'message': '请求微信服务器失败'}), 500

    wechat_response = response.json()

    if 'errcode' in wechat_response and wechat_response['errcode'] != 0:
        return jsonify({'success': False, 'message': wechat_response['errmsg']}), 500

    # 提取 openId 和 sessionKey
    open_id = wechat_response.get('openid')
    session_key = wechat_response.get('session_key')

    if not open_id or not session_key:
        return jsonify({'success': False, 'message': '未能从微信服务器获取 openId 或 sessionKey'}), 500

    # 生成自定义的登录态（JWT）
    custom_token = generate_custom_token(open_id, session_key)

    # 返回自定义的登录态
    return jsonify({
        'success': True,
        'openId': open_id,
        'sessionKey': session_key,
        'customToken': custom_token
    })

def generate_custom_token(open_id, session_key):
    # 生成 JWT
    payload = {
        'openId': open_id,
        'sessionKey': session_key,
        'exp': int(time.time()) + 3600  # 令牌有效期为1小时
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

if __name__ == '__main__':
    app.run(debug=True)