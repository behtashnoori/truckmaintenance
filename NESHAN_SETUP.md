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

## توجه

این پروژه **فقط** از سرویس نشان برای مسیریابی استفاده می‌کند. سایر سرویس‌های مسیریابی (Google Maps، Balad، Map.ir) حذف شده‌اند.

