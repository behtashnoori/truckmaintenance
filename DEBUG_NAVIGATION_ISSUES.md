# 🔧 راهنمای عیب‌یابی مسیریابی نشان

## 🚨 مشکل: مقادیر NaN در مودال مسیریابی

### علائم مشکل
- در مودال مسیریابی، مسافت و زمان "NaN" نمایش داده می‌شود
- خطای `net::ERR_TIMED_OUT` در کنسول
- عدم دریافت پاسخ از API نشان

### 🔍 مراحل عیب‌یابی

#### مرحله 1: بررسی کنسول مرورگر

1. **F12** را فشار دهید تا Developer Tools باز شود
2. به تب **Console** بروید
3. مودال مسیریابی را باز کنید
4. پیام‌های زیر را جستجو کنید:

```javascript
// پیام‌های مفید برای عیب‌یابی:
"Neshan API Request:" // درخواست API
"Neshan API Response Status:" // وضعیت پاسخ
"Neshan API Response Data:" // داده‌های دریافتی
"Error fetching route from Neshan:" // خطاهای API
"Using fallback calculation:" // محاسبه جایگزین
```

#### مرحله 2: تست مستقیم API

1. به صفحه تست بروید: `http://localhost:5173/test-navigation`
2. روی دکمه **"تست مستقیم API"** کلیک کنید
3. نتیجه را در کنسول بررسی کنید

#### مرحله 3: بررسی کلید API

```javascript
// در کنسول مرورگر اجرا کنید:
console.log('API Key:', import.meta.env.VITE_NESHAN_API_KEY);
```

کلید باید: `service.d39f79de30c34282b0a48564ff3b8b13` باشد

#### مرحله 4: تست دستی API

```javascript
// در کنسول مرورگر اجرا کنید:
fetch('https://api.neshan.org/v4/direction?type=car&origin=35.6892,51.3890&destination=35.7219,51.3347', {
  headers: {
    'Api-Key': 'service.d39f79de30c34282b0a48564ff3b8b13'
  }
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

### 🛠️ راه‌حل‌های احتمالی

#### راه‌حل 1: مشکل CORS
اگر خطای CORS دریافت می‌کنید:

```javascript
// در vite.config.ts اضافه کنید:
server: {
  proxy: {
    '/neshan-api': {
      target: 'https://api.neshan.org',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/neshan-api/, ''),
    }
  }
}
```

#### راه‌حل 2: تغییر Endpoint API
ممکن است endpoint اشتباه باشد:

```typescript
// در src/config/neshan.ts امتحان کنید:
API_BASE_URL: 'https://platform.neshan.org/api/v4'
// یا
API_BASE_URL: 'https://api.neshan.org/v1'
```

#### راه‌حل 3: استفاده از Fallback
اگر API کار نمی‌کند، از محاسبه محلی استفاده کنید:

```typescript
// در NavigationService.getRoute() 
// fallback calculation فعال است
const distance = this.calculateDistance(originLat, originLon, destLat, destLon) * 1000;
const duration = Math.round(distance / 1000 * 60);
```

### 📊 تست‌های مختلف

#### تست 1: بررسی موقعیت کاربر
```javascript
// در کنسول:
navigator.geolocation.getCurrentPosition(
  pos => console.log('موقعیت:', pos.coords.latitude, pos.coords.longitude),
  err => console.error('خطا:', err)
);
```

#### تست 2: بررسی شبکه
```javascript
// در کنسول:
fetch('https://api.neshan.org/v4/direction?type=car&origin=35.6892,51.3890&destination=35.7219,51.3347')
  .then(r => console.log('وضعیت:', r.status))
  .catch(e => console.error('خطای شبکه:', e));
```

#### تست 3: بررسی کلید API
```javascript
// در کنسول:
fetch('https://api.neshan.org/v4/direction?type=car&origin=35.6892,51.3890&destination=35.7219,51.3347', {
  headers: { 'Api-Key': 'service.d39f79de30c34282b0a48564ff3b8b13' }
})
.then(r => {
  console.log('وضعیت:', r.status);
  return r.text();
})
.then(text => console.log('پاسخ:', text));
```

### 🎯 راه‌حل‌های فوری

#### اگر API نشان کار نمی‌کند:

1. **استفاده از محاسبه محلی:**
   - NavigationService به صورت خودکار از Haversine formula استفاده می‌کند
   - مسافت و زمان تقریبی محاسبه می‌شود

2. **باز کردن نشان بدون اطلاعات مسیر:**
   - دکمه "باز کردن در نشان" همچنان کار می‌کند
   - نشان خودش مسیر را محاسبه می‌کند

3. **تست با مکان‌های مختلف:**
   - از مکان‌های پیش‌فرض در صفحه تست استفاده کنید
   - ممکن است مشکل فقط برای مکان‌های خاص باشد

### 📝 لاگ‌های مفید

```javascript
// برای debug بیشتر، این کد را در کنسول اجرا کنید:
window.testNeshanAPI = async () => {
  const response = await fetch('https://api.neshan.org/v4/direction?type=car&origin=35.6892,51.3890&destination=35.7219,51.3347', {
    headers: { 'Api-Key': 'service.d39f79de30c34282b0a48564ff3b8b13' }
  });
  console.log('Status:', response.status);
  console.log('Headers:', Object.fromEntries(response.headers.entries()));
  const data = await response.json();
  console.log('Data:', data);
  return data;
};

// سپس اجرا کنید:
testNeshanAPI();
```

### 🔗 لینک‌های مفید

- **صفحه تست:** `http://localhost:5173/test-navigation`
- **مستندات نشان:** [platform.neshan.org](https://platform.neshan.org)
- **پنل توسعه‌دهندگان:** [platform.neshan.org/panel](https://platform.neshan.org/panel)

### ⚡ نکات مهم

1. **HTTPS:** برای دسترسی به geolocation از HTTPS یا localhost استفاده کنید
2. **موقعیت مکانی:** دسترسی به موقعیت را در مرورگر فعال کنید
3. **پاپ‌آپ بلاکر:** برای باز شدن نشان، پاپ‌آپ بلاکر را غیرفعال کنید
4. **شبکه:** اتصال اینترنت پایدار داشته باشید

### 🎯 نتیجه‌گیری

اگر همه راه‌حل‌ها کار نکرد:
1. از محاسبه محلی (fallback) استفاده کنید
2. مسیریابی در نشان همچنان کار می‌کند
3. کاربر می‌تواند از نشان برای مسیریابی استفاده کند

**مهم:** حتی اگر API کار نکند، قابلیت مسیریابی همچنان مفید است!
