# API مدیریت شرکت‌ها (Company Management API)

## نمای کلی
این API برای مدیریت شرکت‌های ارائه‌دهنده خدمات طراحی شده است. فقط کارشناسان بازرگانی و مدیران (Admins) می‌توانند از این endpoint استفاده کنند.

---

## POST /api/company
ایجاد شرکت جدید

### احراز هویت
✅ نیاز به توکن JWT  
✅ نقش مجاز: `business_expert`, `admin`

### Headers
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Request Body

#### فرمت اول (استاندارد):
```json
{
  "name": "شرکت نمونه",
  "phone": "09123456789"
}
```

#### فرمت دوم (فیلدهای جایگزین):
```json
{
  "companyName": "شرکت نمونه",
  "tel": "09123456789"
}
```

### پارامترها

| پارامتر | نوع | الزامی | توضیحات |
|---------|-----|--------|---------|
| `name` یا `companyName` | string | بله | نام شرکت |
| `phone` یا `tel` | string | بله | شماره موبایل (فرمت: 09xxxxxxxxx) |

### قوانین اعتبارسنجی

1. **نام شرکت:**
   - نمی‌تواند خالی باشد
   - از کاراکترهای مخرب پاکسازی می‌شود (XSS Protection)

2. **شماره تلفن:**
   - باید با 09 شروع شود
   - باید دقیقاً 11 رقم باشد
   - فقط اعداد مجاز است
   - باید منحصر به فرد باشد (Unique)

3. **فیلدهای مجاز:**
   - فقط `name`, `companyName`, `phone`, `tel` مجاز هستند
   - فیلدهای اضافی رد می‌شوند

### پاسخ‌ها

#### ✅ موفق (201 Created)
```json
{
  "id": 1,
  "message": "company created"
}
```

#### ❌ خطا: فیلد الزامی گم شده (400 Bad Request)
```json
{
  "error": "name و phone الزامی هستند"
}
```

#### ❌ خطا: فرمت نامعتبر شماره تلفن (400 Bad Request)
```json
{
  "error": "فرمت شماره تلفن نامعتبر است"
}
```

#### ❌ خطا: فیلدهای اضافی (400 Bad Request)
```json
{
  "error": "Extra fields not allowed: ['extra_field']"
}
```

#### ❌ خطا: شماره تلفن تکراری (409 Conflict)
```json
{
  "error": "شرکت با این شماره تلفن قبلاً ثبت شده است"
}
```

#### ❌ خطا: عدم احراز هویت (401 Unauthorized)
```json
{
  "message": "Token is missing"
}
```
یا
```json
{
  "message": "Token is invalid"
}
```

#### ❌ خطا: عدم مجوز (403 Forbidden)
```json
{
  "message": "Business expert access required"
}
```

#### ❌ خطا: خطای سرور (500 Internal Server Error)
```json
{
  "error": "<error message>"
}
```

---

## نمونه‌های استفاده

### cURL
```bash
curl -X POST http://localhost:5000/api/company \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "شرکت خدمات فنی پارس",
    "phone": "09123456789"
  }'
```

### Python (requests)
```python
import requests

url = "http://localhost:5000/api/company"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "name": "شرکت خدمات فنی پارس",
    "phone": "09123456789"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### JavaScript (fetch)
```javascript
fetch('http://localhost:5000/api/company', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'شرکت خدمات فنی پارس',
    phone: '09123456789'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## جزئیات فنی

### مدل دیتابیس
شرکت با مقادیر پیش‌فرض زیر ایجاد می‌شود:

```python
Company(
    name="<user_input>",
    phone_mobile="<user_input>",
    address="",              # خالی
    latitude=0.0,            # مقدار پیش‌فرض
    longitude=0.0,           # مقدار پیش‌فرض
    is_active=True           # فعال
)
```

### محدودیت‌ها
- محدودیت UNIQUE روی `phone_mobile`
- فیلدهای `name`, `address`, `phone_mobile` الزامی هستند
- فیلد `phone_landline` اختیاری است

### امنیت

1. **احراز هویت:**
   - استفاده از JWT Token
   - بررسی اعتبار توکن
   - بررسی انقضای توکن

2. **مجوزدهی:**
   - بررسی نقش کاربر (business_expert یا admin)
   - بررسی وضعیت فعال بودن کاربر

3. **اعتبارسنجی:**
   - پاکسازی ورودی برای جلوگیری از XSS
   - استفاده از ORM برای جلوگیری از SQL Injection
   - اعتبارسنجی فرمت داده‌ها

---

## کدهای وضعیت HTTP

| کد | معنی | استفاده |
|----|------|----------|
| 201 | Created | شرکت با موفقیت ایجاد شد |
| 400 | Bad Request | ورودی نامعتبر یا فیلد گم شده |
| 401 | Unauthorized | توکن گم شده یا نامعتبر |
| 403 | Forbidden | کاربر مجوز ندارد |
| 409 | Conflict | شماره تلفن تکراری |
| 500 | Internal Server Error | خطای سرور |

---

## نکات مهم

1. شماره تلفن باید منحصر به فرد باشد
2. از هر دو فرمت نام فیلد (`name`/`companyName` و `phone`/`tel`) پشتیبانی می‌شود
3. شرکت به صورت پیش‌فرض فعال (`is_active=True`) ایجاد می‌شود
4. موقعیت جغرافیایی (latitude, longitude) ابتدا صفر است و باید بعداً به‌روزرسانی شود
5. آدرس ابتدا خالی است و باید بعداً پر شود

---

## تغییرات آینده پیشنهادی

1. اضافه کردن فیلدهای اختیاری بیشتر در request:
   - `address`
   - `latitude`
   - `longitude`
   - `phone_landline`

2. اضافه کردن اعتبارسنجی تلفن ثابت

3. اضافه کردن قابلیت آپلود لوگو شرکت

4. اضافه کردن قابلیت انتخاب دسته‌بندی (categories) هنگام ایجاد

---

**نسخه API:** 1.0  
**آخرین به‌روزرسانی:** 2025-10-08

