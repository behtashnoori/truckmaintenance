# راهنمای پیکربندی نشان (Neshan Map)

## کلید API نشان

کلید API نشان شما: `service.d39f79de30c34282b0a48564ff3b8b13`

## نحوه استفاده

### 1. تنظیم متغیر محیطی (Environment Variable)

برای استفاده از کلید نشان، یک فایل `.env` در ریشه پروژه ایجاد کنید:

```bash
# .env
VITE_NESHAN_API_KEY=service.d39f79de30c34282b0a48564ff3b8b13
```

⚠️ **نکته مهم**: فایل `.env` در `.gitignore` قرار دارد و به گیت آپلود نمی‌شود.

### 2. استفاده در کد

کلید API به صورت خودکار از فایل تنظیمات نشان (`src/config/neshan.ts`) بارگذاری می‌شود:

```typescript
import NESHAN_CONFIG from '@/config/neshan';

// کلید API به صورت خودکار در دسترس است
const apiKey = NESHAN_CONFIG.API_KEY;
```

### 3. قابلیت‌های پیاده‌سازی شده

#### مسیریابی با API نشان
- دریافت مسیر واقعی از API نشان
- نمایش مسافت دقیق (متر/کیلومتر)
- نمایش زمان تقریبی سفر (دقیقه/ساعت)
- باز کردن مسیریابی در اپلیکیشن/وب نشان

#### انواع وسیله نقلیه
سرویس از انواع زیر پشتیبانی می‌کند:
- `car` - خودرو (پیش‌فرض)
- `motorcycle` - موتورسیکلت
- `taxi` - تاکسی

### 4. نحوه استفاده در کامپوننت‌ها

```typescript
import { NavigationService } from '@/services/navigation';

// دریافت مسیر از نشان
const route = await NavigationService.getRoute(
  originLat,    // عرض جغرافیایی مبدا
  originLon,    // طول جغرافیایی مبدا
  destLat,      // عرض جغرافیایی مقصد
  destLon,      // طول جغرافیایی مقصد
  'car'         // نوع وسیله (اختیاری)
);

// باز کردن نشان برای مسیریابی
await NavigationService.openNeshan({
  lat: 35.7219,           // مقصد
  lon: 51.3347,
  label: 'نام مقصد',
  originLat: 35.6892,     // مبدا (اختیاری)
  originLon: 51.3890
});
```

### 5. کامپوننت NavigationModal

این کامپوننت به صورت خودکار:
1. موقعیت فعلی کاربر را دریافت می‌کند
2. از API نشان مسیر را محاسبه می‌کند
3. مسافت و زمان واقعی را نمایش می‌دهد
4. دکمه مسیریابی در نشان را فراهم می‌کند

```typescript
import { NavigationModal } from '@/components/NavigationModal';

<NavigationModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  providerLocation={{ lat: 35.7219, lon: 51.3347 }}
  providerName="نام ارائه‌دهنده"
/>
```

## API Endpoints

### مسیریابی (Direction/Routing)
```
GET https://api.neshan.org/v4/direction
Parameters:
  - type: car | motorcycle | taxi
  - origin: lat,lon (مبدا)
  - destination: lat,lon (مقصد)

Headers:
  - Api-Key: YOUR_API_KEY
```

### پاسخ API
```json
{
  "routes": [{
    "distance": 5420,        // متر
    "duration": 980,         // ثانیه
    "legs": [{
      "distance": 5420,
      "duration": 980,
      "steps": [...]
    }]
  }]
}
```

## لینک‌های مفید

- [مستندات API نشان](https://platform.neshan.org/api/docs)
- [پنل توسعه‌دهندگان نشان](https://platform.neshan.org/panel)
- [وب‌سایت نشان](https://neshan.org)

## رفع مشکلات رایج

### خطای 401 (Unauthorized)
- کلید API را بررسی کنید
- اطمینان حاصل کنید که `.env` فایل در مسیر درست قرار دارد
- سرور را مجدداً راه‌اندازی کنید

### عدم دریافت مسیر
- اتصال اینترنت را بررسی کنید
- محدودیت‌های API (rate limit) را چک کنید
- مختصات جغرافیایی را بررسی کنید

### مسیریابی باز نمی‌شود
- دسترسی به موقعیت مکانی را در مرورگر فعال کنید
- از HTTPS استفاده کنید (برای دسترسی به geolocation)
- پاپ‌آپ بلاکر را غیرفعال کنید

## Deep Links برای اپلیکیشن موبایل

### پشتیبانی از اپلیکیشن نشان در موبایل

سیستم به صورت خودکار نوع دستگاه را تشخیص داده و رفتار مناسب را انجام می‌دهد:

#### Android
- **Deep Link**: `nshn://routes?type=car&origin=LAT,LON&destination=LAT,LON`
- اگر اپلیکیشن نشان نصب باشد، مستقیماً باز می‌شود
- اگر نصب نباشد، پس از 2 ثانیه به وب نشان هدایت می‌شود

#### iOS  
- **Deep Link**: `neshan://routes?type=car&origin=LAT,LON&destination=LAT,LON`
- اگر اپلیکیشن نشان نصب باشد، مستقیماً باز می‌شود
- اگر نصب نباشد، پس از 2 ثانیه به وب نشان هدایت می‌شود

#### Desktop/Laptop
- همیشه وب نشان در تب جدید باز می‌شود
- URL: `https://neshan.org/maps/routes?type=car&origin=LAT,LON&destination=LAT,LON`

### تست در محیط توسعه

#### روش 1: Chrome DevTools Device Mode
1. در Chrome، `F12` را بزنید تا DevTools باز شود
2. دکمه Device Toggle را فعال کنید (Ctrl+Shift+M)
3. یک دستگاه موبایل (مثل iPhone یا Galaxy S20) را انتخاب کنید
4. صفحه را refresh کنید
5. روی دکمه مسیریابی کلیک کنید

#### روش 2: تست در دستگاه واقعی
1. سرور را روی شبکه محلی اجرا کنید
2. از IP سیستم (مثل `192.168.1.100:5173`) در موبایل استفاده کنید
3. اگر اپلیکیشن نشان نصب باشد، باز می‌شود
4. در غیر این صورت، وب نشان باز می‌شود

#### روش 3: Override User Agent (برای تست سریع)
در Console مرورگر:
```javascript
Object.defineProperty(navigator, 'userAgent', {
  get: () => 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/91.0.4472.120 Mobile Safari/537.36'
});
```

### نحوه استفاده در کد

```typescript
// تشخیص نوع دستگاه
const isMobile = NavigationService.isMobileDevice();
const isAndroid = NavigationService.isAndroid();
const isIOS = NavigationService.isIOS();

// باز کردن مسیریابی (به صورت خودکار نوع دستگاه را تشخیص می‌دهد)
await NavigationService.openNeshan({
  lat: 35.7219,
  lon: 51.3347,
  label: 'نام مقصد',
  originLat: 35.6892,  // اختیاری
  originLon: 51.3890
});
```

## توجه

این پروژه **فقط** از سرویس نشان برای مسیریابی استفاده می‌کند. سایر سرویس‌های مسیریابی (Google Maps، Balad، Map.ir) حذف شده‌اند.

### ویژگی‌های کلیدی
- ✅ تشخیص خودکار نوع دستگاه (موبایل/دسکتاپ)
- ✅ پشتیبانی از Deep Links برای اپلیکیشن نشان
- ✅ فال‌بک خودکار به وب نشان
- ✅ دریافت موقعیت لحظه‌ای کاربر
- ✅ محاسبه مسیر واقعی از API نشان
- ✅ نمایش مسافت و زمان دقیق

