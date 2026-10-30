1. Chạy lệnh tạo môi trường và cài thư viện
    
    ```python
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    

---

2. Chạy lệnh setup .env
    1. Tạo file .env
        
        ```python
        cp .env.example .env # copy ra
        # hoặc
        touch .env # tạo mới
        ```
        
    2. Chạy lệnh tạo JWT Secret Key rồi copy vào
        
        ```python
        python3 -c "import secrets; print(secrets.token_hex(32))"
        ```
        
    3. File .env hoàn chỉnh
        
        ```python
        JWT_SECRET=7ba8364368b70...
        JWT_ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=5
        REFRESH_TOKEN_EXPIRE_DAYS=7
        
        DB_USER=root
        DB_PASSWORD=
        DB_HOST=localhost
        DB_PORT=3306
        DB_NAME=tuition_payment_system
        ```
        

---

3. Chạy migration 
    1. Mỗi khi có models mới muốn tạo migration phải vào file **`Migrations/env.py`** để khai báo nó mới nhận rồi sẽ autogen được các cột mà không cần phải viết tay.
        
        ```python
        from config.db import Base, engine
        from Models.user import User
        from Models.transaction import Transaction
        
        target_metadata = Base.metadata
        ```
        
    2. Chạy lệnh tạo migration (nhớ check kĩ các cột vì nó autogen từ model ra)
        
        ```python
        alembic revision --autogenerate -m "create .... table"
        ```
        
    3. Chạy lệnh các migration chưa được chạy (mới tạo mới)
        
        ```python
        alembic upgrade head
        ```
        
---

4. Chạy lệnh init user để thêm user mới login
   ```python
   python -m Console.Commands.init_user
   ```
   
---

5. Start server lên
    
    ```python
    source venv/bin/activate # bật môi trường ảo bật rồi thì thôi
    uvicorn main:app --reload
    ```

---
6. Mở postman lên test
