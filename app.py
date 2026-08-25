# ARAFAT LIKE API SRC UID PASSWORD 
# POWERED BY : @ISHRAKSHADMAN
# CHANNEL : @ISHRAKSHADMAN
# DONT CHANGE CREDIT 

from flask import Flask, request, jsonify
import ssl
import time
import os
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import requests
import json
import like_pb2
import like_count_pb2
import uid_generator_pb2
import urllib3
from datetime import datetime

# Tắt cảnh báo SSL không an toàn
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ==========================================
# HỆ THỐNG XỬ LÝ TOKEN & GỌI API CHO VERCEL
# ==========================================

def load_tokens(server_name):
    """Tải danh sách token dựa theo tên server từ file JSON có sẵn (An toàn trên Vercel Read-only)."""
    try:
        filename = f"token_{server_name.lower()}.json"
        if not os.path.exists(filename):
            filename = "token_vn.json"
            
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        app.logger.error(f"Error loading tokens for server {server_name}: {e}")
    return None

def encrypt_message(plaintext):
    """Mã hóa AES CBC cho chuỗi byte protobuf."""
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return binascii.hexlify(encrypted_message).decode('utf-8')
    except Exception as e:
        app.logger.error(f"Error encrypting message: {e}")
        return None

def create_protobuf_message(user_id, region):
    """Tạo protobuf message cho chức năng Like."""
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        if hasattr(message, 'ob_version'):
            message.ob_version = "OB50"
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating like protobuf message: {e}")
        return None

def send_request_sync(encrypted_uid, token, url):
    """Gửi yêu cầu Like đồng bộ qua requests (Tối ưu cho Serverless để tránh lỗi asyncio event loop)."""
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB50"
        }
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=5)
        if response.status_code != 200:
            return None
        return response.text
    except Exception as e:
        return None

def create_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.krishna_ = int(uid)  
        message.teamXdarks = 1       
        if hasattr(message, 'ob_version'):
            message.ob_version = "OB50"
        return message.SerializeToString()
    except Exception as e:
        return None

def enc(uid):
    protobuf_data = create_protobuf(uid)
    if not protobuf_data:
        return None
    return encrypt_message(protobuf_data)

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except Exception as e:
        return None

def make_request(encrypt, server_name, token):
    try:
        url = "https://clientbp.ggpolarbear.com/GetPlayerPersonalShow"
        edata = bytes.fromhex(encrypt)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB50"
        }
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=5)
        if response.status_code != 200:
            return None
        return decode_protobuf(response.content)
    except Exception as e:
        return None

@app.route('/reload-tokens', methods=['GET', 'POST'])
def reload_tokens():
    """
    Đã sửa tính năng reload token để tương thích với Vercel.
    Vì Vercel là môi trường Read-only (không cho ghi file cục bộ động), 
    bạn cần cập nhật file token_vn.json trực tiếp lên GitHub rồi Redeploy.
    Endpoint này thông báo trạng thái thay vì chạy hàm ghi file gây lỗi 500.
    """
    return jsonify({
        "status": "info", 
        "message": "Môi trường Vercel ở chế độ Read-only. Để cập nhật token mới, hãy đẩy file token_vn.json mới lên GitHub và Redeploy lại dự án!"
    }), 200

@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400

    try:
        tokens = load_tokens(server_name)
        if not tokens:
            return jsonify({"Lỗi": "Không tìm thấy file token_vn.json hoặc file token trống."}), 500
            
        token = tokens[0]['token']
        encrypted_uid = enc(uid)
        if encrypted_uid is None:
            return jsonify({"Lỗi": "Mã hóa UID thất bại."}), 500

        before = make_request(encrypted_uid, server_name, token)
        if before is None:
            return jsonify({"Lỗi": "Không thể truy xuất thông tin người chơi ban đầu."}), 500
            
        jsone = MessageToJson(before)
        data_before = json.loads(jsone)
        before_like = int(data_before.get('AccountInfo', {}).get('Likes', 0))

        url = "https://clientbp.ggpolarbear.com/LikeProfile"
        
        # Gửi tối đa 50 request qua vòng lặp đồng bộ an toàn trên Vercel
        for i in range(min(50, len(tokens))):
            t = tokens[i % len(tokens)]["token"]
            send_request_sync(encrypted_uid, t, url)

        after = make_request(encrypted_uid, server_name, token)
        if after is None:
            return jsonify({"Lỗi": "Không thể lấy thông tin người chơi sau khi Like."}), 500
            
        jsone_after = MessageToJson(after)
        data_after = json.loads(jsone_after)
        
        account_info = data_after.get('AccountInfo', {})
        after_like = int(account_info.get('Likes', 0))
        player_uid = int(account_info.get('UID', 0))
        player_name = str(account_info.get('PlayerNickname', ''))
        
        like_given = after_like - before_like
        status = 1 if like_given != 0 else 2
        
        return jsonify({
            "LikesGivenByAPI": like_given,
            "LikesafterCommand": after_like,
            "LikesbeforeCommand": before_like,
            "PlayerNickname": player_name,
            "UID": player_uid,
            "status": status
        })
    except Exception as e:
        return jsonify({"Lỗi": str(e)}), 500

@app.route('/')
def home():
    return "Free Fire Buff Like API is running successfully on Vercel!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return binascii.hexlify(encrypted_message).decode('utf-8')
    except Exception as e:
        app.logger.error(f"Error encrypting message: {e}")
        return None

def create_protobuf_message(user_id, region):
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        if hasattr(message, 'ob_version'):
            message.ob_version = "OB48"
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating protobuf message: {e}")
        return None

async def send_request(encrypted_uid, token, url):
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB50" #Fixed
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    app.logger.error(f"Request failed with status code: {response.status} and response: {text}")
                    return None
                return await response.text()
    except Exception as e:
        app.logger.error(f"Exception in send_request: {e}")
        return None

async def send_multiple_requests(uid, server_name, url):
    try:
        region = server_name
        protobuf_message = create_protobuf_message(uid, region)
        if protobuf_message is None:
            app.logger.error("Failed to create protobuf message.")
            return None
        encrypted_uid = encrypt_message(protobuf_message)
        if encrypted_uid is None:
            app.logger.error("Encryption failed.")
            return None
        tasks = []
        tokens = load_tokens(server_name)
        if tokens is None:
            app.logger.error("Failed to load tokens.")
            return None
        for i in range(100):
            token = tokens[i % len(tokens)]["token"]
            tasks.append(send_request(encrypted_uid, token, url))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    except Exception as e:
        app.logger.error(f"Exception in send_multiple_requests: {e}")
        return None

def create_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
 
        if hasattr(message, 'ob_version'):
            message.ob_version = "OB48"
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating uid protobuf: {e}")
        return None

def enc(uid):
    protobuf_data = create_protobuf(uid)
    if protobuf_data is None:
        return None
    encrypted_uid = encrypt_message(protobuf_data)
    return encrypted_uid

def make_request(encrypt, server_name, token):
    try:
        if server_name == "VN":
            url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
        elif server_name in {"VN", "VN", "VN", "VN"}:
            url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
        else:
            url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
        edata = bytes.fromhex(encrypt)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB50"
        }
        response = requests.post(url, data=edata, headers=headers, verify=False)
        if response.status_code != 200:
            app.logger.error(f"Request failed with status code: {response.status_code} and response: {response.text}")
            return None
        binary = response.content
        decode = decode_protobuf(binary)
        if decode is None:
            app.logger.error("Protobuf decoding returned None.")
        return decode
    except Exception as e:
        app.logger.error(f"Error in make_request: {e}")
        return None

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except DecodeError as e:
        app.logger.error(f"Error decoding Protobuf data: {e}")
        return None
    except Exception as e:
        app.logger.error(f"Unexpected error during protobuf decoding: {e}")
        return None

@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400

    try:
        def process_request():
            tokens = load_tokens(server_name)
            if tokens is None:
                raise Exception("Failed to load tokens.")
            token = tokens[0]['token']
            encrypted_uid = enc(uid)
            if encrypted_uid is None:
                raise Exception("Encryption of UID failed.")

            before = make_request(encrypted_uid, server_name, token)
            if before is None:
                raise Exception("Failed to retrieve initial player info.")
            try:
                jsone = MessageToJson(before)
            except Exception as e:
                raise Exception(f"Error converting 'before' protobuf to JSON: {e}")
            data_before = json.loads(jsone)
            before_like = data_before.get('AccountInfo', {}).get('Likes', 0)
            try:
                before_like = int(before_like)
            except Exception:
                before_like = 0
            app.logger.info(f"Likes before command: {before_like}")

            if server_name == "VN":
                url = "https://clientbp.ggblueshark.com/LikeProfile"
            elif server_name in {"VN", "VN", "VN", "VN"}:
                url = "https://clientbp.ggblueshark.com/LikeProfile"
            else:
                url = "https://clientbp.ggblueshark.com/LikeProfile"

            asyncio.run(send_multiple_requests(uid, server_name, url))

            after = make_request(encrypted_uid, server_name, token)
            if after is None:
                raise Exception("Failed to retrieve player info after like requests.")
            try:
                jsone_after = MessageToJson(after)
            except Exception as e:
                raise Exception(f"Error converting 'after' protobuf to JSON: {e}")
            data_after = json.loads(jsone_after)
            after_like = int(data_after.get('AccountInfo', {}).get('Likes', 0))
            player_uid = int(data_after.get('AccountInfo', {}).get('UID', 0))
            player_name = str(data_after.get('AccountInfo', {}).get('PlayerNickname', ''))
            like_given = after_like - before_like
            status = 1 if like_given != 0 else 2
            result = {
                "LikesGivenByAPI": like_given,
                "LikesafterCommand": after_like,
                "LikesbeforeCommand": before_like,
                "PlayerNickname": player_name,
                "UID": player_uid,
                "status": status
            }
            return result

        result = process_request()
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
