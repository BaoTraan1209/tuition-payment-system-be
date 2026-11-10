# iBanking – Tuition Payment System

Hệ thống quản lý và thanh toán học phí, gồm giao diện React/Vite, Backend FastAPI, MySQL, Redis và tích hợp OTP qua email, VNPAY Sandbox. Project hỗ trợ đăng nhập sinh viên, quản trị học phí và theo dõi giao dịch.

## 1. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI, Uvicorn |
| Database | MySQL 8 |
| Cache / dịch vụ hỗ trợ | Redis |
| Migration | SQLAlchemy, Alembic |
| Xác thực | JWT |
| Thanh toán | VNPAY Sandbox, email OTP |
| Triển khai | Docker, Docker Compose |

## 2. Cấu trúc thư mục

```text
tuition-payment-system/
├── docker-compose.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── Migrations/
│   ├── Models/
│   ├── Controllers/
│   ├── Services/
│   ├── Console/Commands/
│   ├── .env.example
│   └── Dockerfile
└── frontend/
    ├── package.json
    ├── src/
    └── Dockerfile
```

## 3. Cách 1 – Chạy toàn bộ project bằng Docker (khuyến nghị)

### 3.1. Yêu cầu

- Cài Docker Desktop và mở Docker Desktop trước khi chạy.
- Có source code với các thư mục `backend/`, `frontend/` và file `docker-compose.yml` cùng cấp.
- Không cần cài MySQL, Python hay Node.js trực tiếp trên máy để chạy bằng Docker.

### 3.2. Cấu hình môi trường

Mở PowerShell tại thư mục gốc của project, tạo file cấu hình Backend nếu chưa có:

```powershell
Copy-Item backend/.env.example backend/.env
```

Nếu đã có `backend/.env` thì giữ lại, không cần tạo lại. Điền các biến cần thiết: `JWT_SECRET`, `MAIL_*`, `VNPAY_*`, `USERNAME_ADMIN`, `PASSWORD_ADMIN`. Không đưa `.env` lên GitHub.

**Lưu ý tương thích Docker:** `backend/main.py` hiện có `load_dotenv(ENV_FILE, override=True)`. Để Docker Compose có thể ghi đè `DB_HOST=mysql`, đổi thành:

```python
load_dotenv(ENV_FILE, override=False)
```

Thay đổi này giúp chạy thủ công vẫn đọc `.env`, còn chạy Docker thì ưu tiên các biến do Compose truyền vào. Không cần đổi `DB_HOST=localhost` trong file `.env` gốc.

Bản Docker Compose demo đang cấu hình MySQL root **không mật khẩu**, chỉ phù hợp chạy cục bộ. Trên máy khác, MySQL cài trong Windows không ảnh hưởng đến MySQL trong container.

### 3.3. Khởi động

```powershell
docker compose up -d --build
```

Kiểm tra:

```powershell
docker compose ps
```

Chờ MySQL sẵn sàng, sau đó áp dụng các migration có sẵn:

```powershell
docker compose exec backend python -m alembic upgrade head
```

Tạo tài khoản sinh viên để kiểm thử (nhập thông tin theo hướng dẫn của chương trình):

```powershell
docker compose exec backend python -m Console.Commands.init_user
```

### 3.4. Truy cập hệ thống

| Dịch vụ | Địa chỉ |
|---|---|
| Frontend | http://localhost:5173 |
| Backend Swagger | http://localhost:8000/docs |
| Backend Health | http://localhost:8000/health |
| MySQL Docker từ máy host | `127.0.0.1:3307` |

Backend trong container kết nối MySQL qua `mysql:3306`, không phải `localhost:3307`.

### 3.5. Xem log và dừng

```powershell
docker compose logs -f backend
docker compose logs -f mysql
```

Dừng và giữ nguyên dữ liệu:

```powershell
docker compose down
```

**Không dùng `docker compose down -v` nếu muốn giữ dữ liệu MySQL.** Dữ liệu MySQL trong Docker độc lập với dữ liệu MySQL trên Windows; migration chỉ tạo bảng, không tự nhập dữ liệu sinh viên/học phí cũ.

## 4. Cách 2 – Chạy thủ công không dùng Docker

### 4.1. Yêu cầu

Cài Python 3.11 (hoặc phiên bản tương thích với `requirements.txt`), Node.js, MySQL và Redis nếu các chức năng của Backend cần Redis.

### 4.2. Cài đặt Backend (Windows PowerShell)

Mở terminal trong thư mục `backend`:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nếu dùng Linux/macOS, lệnh kích hoạt là `source venv/bin/activate`.

### 4.3. Thiết lập `.env`

```powershell
Copy-Item .env.example .env
```

Nếu file đã tồn tại thì không ghi đè. Tạo JWT secret mới:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Ví dụ phần cấu hình cơ bản (thay giá trị mẫu bằng thông tin của bạn):

```dotenv
APP_NAME=iBanking
APP_ENV=local
APP_DEBUG=true
APP_HOST=127.0.0.1
APP_PORT=8000

DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tuition_payment_system

JWT_SECRET=THAY_BANG_CHUOI_BI_MAT_MOI
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Điền thêm cấu hình email OTP, VNPAY Sandbox và Admin từ `.env.example`. Đảm bảo MySQL đã chạy, database `tuition_payment_system` tồn tại và tài khoản MySQL khớp với `.env`.

### 4.4. Chạy migration

Để áp dụng các migration đã có:

```powershell
python -m alembic upgrade head
```

**Chỉ khi thêm/sửa Model và muốn tạo migration mới:** kiểm tra `Migrations/env.py` đã import các Model cần thiết và `target_metadata = Base.metadata`, sau đó chạy:

```powershell
python -m alembic revision --autogenerate -m "describe database changes"
python -m alembic upgrade head
```

Kiểm tra kỹ migration được sinh tự động trước khi áp dụng. Không cần tạo revision mới mỗi lần khởi động project.

### 4.5. Tạo tài khoản sinh viên

```powershell
python -m Console.Commands.init_user
```

Nhập thông tin theo yêu cầu của script. Tài khoản Admin được cấu hình riêng qua các biến Admin trong `.env` nếu Backend đang dùng cơ chế đăng nhập Admin này.

### 4.6. Khởi động Backend

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Kiểm tra http://localhost:8000/docs và http://localhost:8000/health.

### 4.7. Cài đặt và khởi động Frontend

Mở PowerShell khác, tại thư mục `frontend`:

```powershell
cd frontend
npm install
```

Tạo `frontend/.env` nếu cần chỉ định API:

```dotenv
VITE_API_URL=http://localhost:8000
```

Khởi động:

```powershell
npm run dev
```

Mở http://localhost:5173. Backend phải bật CORS cho địa chỉ này (mã nguồn hiện tại đã khai báo localhost:5173).

## 5. Kiểm thử bằng Postman / Swagger

1. Mở Swagger tại http://localhost:8000/docs hoặc Postman.
2. Kiểm tra `GET http://localhost:8000/health`.
3. Thử đăng nhập qua `POST /api/auth/login` với tài khoản đã cấu hình/tạo.
4. Với API yêu cầu xác thực, gửi header `Authorization: Bearer <access_token>`.
5. Kiểm thử các API học phí, OTP, thanh toán và lịch sử giao dịch theo dữ liệu đã tạo.

## 6. Lưu ý về VNPAY và OTP

- OTP email cần SMTP hợp lệ và mật khẩu ứng dụng tương ứng; không lưu thông tin thật trong README.
- VNPAY Sandbox cần cấu hình `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`, `VNPAY_PAYMENT_URL`, `VNPAY_RETURN_URL`, `VNPAY_IPN_URL`.
- Nếu VNPAY cần gọi IPN/Return từ Internet về Backend chạy cục bộ, phải dùng ngrok hoặc tunnel công khai đang hoạt động và cập nhật URL tương ứng.
- Việc chạy Docker **không tự động cấu hình ngrok hoặc đăng ký IPN với VNPAY**.

## 7. Lỗi thường gặp

| Lỗi | Cách kiểm tra |
|---|---|
| Không kết nối được MySQL | Kiểm tra `DB_HOST`: Docker dùng `mysql`, chạy thủ công dùng `localhost`; xem `docker compose logs mysql` |
| Port 8000/5173 đã được sử dụng | Dừng server cũ hoặc đổi port mapping |
| Frontend không gọi được API | Kiểm tra `VITE_API_URL`, trạng thái Backend và CORS |
| `No module named ...` | Kiểm tra đã cài `requirements.txt` và kích hoạt đúng môi trường Python |
| Bảng database chưa tồn tại | Chạy `python -m alembic upgrade head` ở môi trường phù hợp |
| VNPAY không cập nhật trạng thái | Kiểm tra URL tunnel, IPN/Return và log Backend |

## 8. Bảo mật

- Không commit `.env`, JWT secret, mật khẩu email, VNPAY hash secret hoặc mật khẩu Admin lên GitHub.
- Đổi mới các khóa/mật khẩu đã từng bị chia sẻ công khai.
- MySQL root không mật khẩu chỉ dùng cho demo cục bộ; khi triển khai thật phải cấu hình tài khoản và mật khẩu an toàn.
