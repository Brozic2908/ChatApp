# Hybrid Chat Application - Hướng Dẫn Sử Dụng

## 📋 Tổng quan

Ứng dụng chat hybrid kết hợp mô hình **Client-Server** và **Peer-to-Peer (P2P)** để quản lý kênh chat và giao tiếp trực tiếp giữa các peers.

### Kiến trúc

```
                ┌──────────────────────────────┐
                │          Client(s)           │
                │  (Browser / Chat App UI)     │
                └─────────────┬────────────────┘
                              │  HTTP Request
                              ▼
                    ┌────────────────────┐
                    │     Proxy Server   │
                    │ (start_proxy.py)   │
                    │ - Lắng nghe cổng 8080
                    │ - Đọc proxy.conf   |
                    │ - Chuyển tiếp yêu cầu đến backend hoặc webapp
                    └──────────┬─────────┘
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
   ┌─────────────────────┐       ┌─────────────────────┐
   │     Backend Server  │       │   WebApp (WeApRous) │
   │ (start_backend.py)  │       │ (start_sampleapp.py)│
   │ - Cổng 9000         │       │ - Cổng 8000         │
   │ - Xử lý logic HTTP  │       │ - RESTful API (chat)│
   │   + cookie session  │       │ - /login, /hello,   │
   │   + kiểm tra auth   │       │   /connect-peer,... │
   └──────────┬──────────┘       └──────────┬──────────┘
              │                             │
              ▼                             ▼
   ┌─────────────────────────────┐   ┌─────────────────────────────┐
   │    Peer-to-Peer (P2P) Chat  │   │   Peer-to-Peer (P2P) Chat   │
   │  ┌──────────────────────┐   │   │  ┌──────────────────────┐   │
   │  │ Peer A (client)      │◄──┼──►│  │ Peer B (client)      │   │
   │  │ - Đã đăng ký tracker │   │   │  │ - Nhận danh sách peers │ │
   │  │ - Chat trực tiếp     │   │   │  │ - Gửi/nhận broadcast   │ │
   │  └──────────────────────┘   │   │  └──────────────────────┘   │
   └─────────────────────────────┘   └─────────────────────────────┘
```

## 🚀 Cài đặt và chạy

### Bước 1: Chuẩn bị môi trường

1. Copy file `start_chatapp.py` vào thư mục gốc của project (cùng cấp với `start_backend.py`)

2. Đảm bảo cấu trúc thư mục:

```
your_project/
├── daemon/
│   ├── __init__.py
│   ├── backend.py
│   ├── weaprous.py
│   ├── request.py
│   ├── response.py
│   └── ...
├── start_backend.py
├── start_chatapp.py  ← File mới
└── www/
    └── chat_client.html  ← File test client
```

### Bước 2: Khởi động server

Chạy lệnh sau trong terminal:

```bash
python start_chatapp.py --server-ip 0.0.0.0 --server-port 8001
```

Hoặc với IP cụ thể:

```bash
python start_chatapp.py --server-ip 127.0.0.1 --server-port 8001
```

Bạn sẽ thấy output:

```
[ChatApp] Starting hybrid chat server on 127.0.0.1:8001
[Backend] Listening on port 8001
```

### Bước 3: Test với HTML client

1. Mở file `chat_client.html` trong trình duyệt
2. Hoặc đặt file vào thư mục `www/` và truy cập qua backend server chính

## 📡 API Endpoints

### 1. **POST /submit-info** - Đăng ký Peer

Đăng ký một peer mới với server trung tâm.

**Request:**

```json
{
  "peer_id": "peer123",
  "ip": "192.168.1.100",
  "port": 5000
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Peer registered",
  "peer_id": "peer123"
}
```

**Test với curl:**

```bash
curl -X POST http://localhost:8001/submit-info \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer001","ip":"127.0.0.1","port":5000}'
```

---

### 2. **GET /get-list** - Lấy danh sách Peers

Lấy danh sách tất cả peers đang hoạt động.

**Response:**

```json
{
  "status": "success",
  "peers": [
    {
      "peer_id": "peer123",
      "ip": "192.168.1.100",
      "port": 5000,
      "last_seen": "2025-11-05T10:30:00"
    }
  ],
  "count": 1
}
```

**Test với curl:**

```bash
curl http://localhost:8001/get-list
```

---

### 3. **POST /add-list** - Tham gia Channel

Thêm peer vào một channel chat.

**Request:**

```json
{
  "peer_id": "peer123",
  "channel": "general"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Added to channel general",
  "channel": "general",
  "members_count": 3
}
```

**Test với curl:**

```bash
curl -X POST http://localhost:8001/add-list \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer001","channel":"general"}'
```

---

### 4. **POST /connect-peer** - Kết nối P2P

Lấy thông tin để thiết lập kết nối P2P với peer khác.

**Request:**

```json
{
  "from_peer": "peer123",
  "to_peer": "peer456"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Peer info retrieved",
  "peer_info": {
    "peer_id": "peer456",
    "ip": "192.168.1.101",
    "port": 5001
  }
}
```

---

### 5. **POST /broadcast-peer** - Broadcast tin nhắn

Gửi tin nhắn đến tất cả peers trong channel.

**Request:**

```json
{
  "peer_id": "peer123",
  "channel": "general",
  "message": "Hello everyone!"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Message broadcasted",
  "recipients": ["peer456", "peer789"],
  "channel": "general"
}
```

**Test với curl:**

```bash
curl -X POST http://localhost:8001/broadcast-peer \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer001","channel":"general","message":"Hello!"}'
```

---

### 6. **POST /send-peer** - Gửi tin nhắn trực tiếp

Gửi tin nhắn trực tiếp đến một peer cụ thể.

**Request:**

```json
{
  "from_peer": "peer123",
  "to_peer": "peer456",
  "message": "Hi there!"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Message sent",
  "peer_info": {
    "peer_id": "peer456",
    "ip": "192.168.1.101",
    "port": 5001
  }
}
```

---

### 7. **GET /get-messages** - Lấy tin nhắn trong channel

Lấy tất cả tin nhắn trong một channel.

**Request Body:**

```json
{
  "channel": "general"
}
```

**Response:**

```json
{
  "status": "success",
  "channel": "general",
  "messages": [
    {
      "from": "peer123",
      "message": "Hello everyone!",
      "timestamp": "2025-11-05T10:35:00"
    }
  ],
  "count": 1
}
```

## 🧪 Test Scenarios

### Scenario 1: Đăng ký và khám phá Peers

```bash
# Đăng ký peer 1
curl -X POST http://localhost:8001/submit-info \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer001","ip":"127.0.0.1","port":5000}'

# Đăng ký peer 2
curl -X POST http://localhost:8001/submit-info \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer002","ip":"127.0.0.1","port":5001}'

# Lấy danh sách peers
curl http://localhost:8001/get-list
```

### Scenario 2: Tham gia Channel và Broadcast

```bash
# Peer 1 join channel
curl -X POST http://localhost:8001/add-list \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer001","channel":"general"}'

# Peer 2 join channel
curl -X POST http://localhost:8001/add-list \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer002","channel":"general"}'

# Peer 1 broadcast message
curl -X POST http://localhost:8001/broadcast-peer \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer001","channel":"general","message":"Hello everyone!"}'

# Lấy tin nhắn
curl -X POST http://localhost:8001/get-messages \
  -H "Content-Type: application/json" \
  -d '{"channel":"general"}'
```

### Scenario 3: P2P Direct Message

```bash
# Connect to peer
curl -X POST http://localhost:8001/connect-peer \
  -H "Content-Type: application/json" \
  -d '{"from_peer":"peer001","to_peer":"peer002"}'

# Send direct message
curl -X POST http://localhost:8001/send-peer \
  -H "Content-Type: application/json" \
  -d '{"from_peer":"peer001","to_peer":"peer002","message":"Private message"}'
```

## 📝 Ghi chú quan trọng

### Concurrency

- Server sử dụng threading để xử lý nhiều client đồng thời
- Mỗi request được handle trong thread riêng biệt (xem `backend.py`)

### Error Handling

- Tất cả endpoints đều có try-catch để bắt lỗi
- Trả về JSON với `status: "error"` khi có lỗi
- Log chi tiết trên console server

### Protocol Design

- Sử dụng HTTP POST cho các thao tác ghi (registration, send message)
- Sử dụng HTTP GET cho các thao tác đọc (get peers, get messages)
- Tất cả data được encode JSON
- Response format thống nhất: `{"status": "...", "message": "...", ...}`

### Security Notes

- ⚠️ Đây là bài tập học tập, không có authentication thực sự
- Production cần thêm: SSL/TLS, token-based auth, input validation
- Không có rate limiting hoặc DDoS protection

## 🔧 Mở rộng

### Thêm authentication

Sửa trong `start_chatapp.py`:

```python
def verify_peer_token(token):
    # Implement your token verification
    return True

@app.route('/submit-info', methods=['POST'])
def submit_peer_info(headers="", body=""):
    token = headers.get('Authorization', '')
    if not verify_peer_token(token):
        return {"status": "error", "message": "Unauthorized"}
    # ... rest of code
```

### Persistent Storage

Thay thế in-memory storage bằng database:

```python
import sqlite3

# Thay vì:
peers_registry = {}

# Sử dụng:
def save_peer(peer_id, ip, port):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO peers VALUES (?, ?, ?)",
        (peer_id, ip, port)
    )
    conn.commit()
    conn.close()
```

## 🐛 Troubleshooting

### Lỗi "Address already in use"

```bash
# Tìm và kill process đang dùng port 8001
lsof -ti:8001 | xargs kill -9
```

### Không kết nối được

- Kiểm tra firewall
- Thử với `127.0.0.1` thay vì `0.0.0.0`
- Xem log console để biết lỗi cụ thể

### JSON parse error

- Đảm bảo Content-Type header là `application/json`
- Kiểm tra format JSON hợp lệ

## 📚 Tài liệu tham khảo

- PEP 8: https://peps.python.org/pep-0008
- PEP 257: https://peps.python.org/pep-0257
- RFC HTTP/1.1: https://www.rfc-editor.org/rfc/rfc2616
