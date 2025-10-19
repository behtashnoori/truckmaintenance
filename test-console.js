// اسکریپت تست سریع برای تشخیص مشکل موقعیت مکانی
// این کد را در Console مرورگر (F12 > Console) کپی و اجرا کنید

console.log('🔍 شروع تست تشخیص موقعیت مکانی...');

// 1. بررسی پشتیبانی
console.log('1️⃣ بررسی پشتیبانی Geolocation:', navigator.geolocation ? '✅ پشتیبانی می‌شود' : '❌ پشتیبانی نمی‌شود');

// 2. بررسی HTTPS
console.log('2️⃣ بررسی HTTPS:', location.protocol === 'https:' ? '✅ HTTPS فعال' : '⚠️ HTTP (مشکل احتمالی)');

// 3. تست دریافت موقعیت
console.log('3️⃣ درخواست موقعیت مکانی...');

navigator.geolocation.getCurrentPosition(
    (position) => {
        console.log('✅ موقعیت دریافت شد:', {
            lat: position.coords.latitude,
            lon: position.coords.longitude,
            accuracy: position.coords.accuracy + ' متر',
            timestamp: new Date(position.timestamp).toLocaleString('fa-IR')
        });
    },
    (error) => {
        console.error('❌ خطا در دریافت موقعیت:', {
            code: error.code,
            message: error.message,
            codes: {
                1: 'PERMISSION_DENIED - دسترسی رد شد',
                2: 'POSITION_UNAVAILABLE - موقعیت در دسترس نیست',
                3: 'TIMEOUT - زمان به پایان رسید'
            }
        });
    },
    {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
    }
);

// 4. اطلاعات مرورگر
console.log('4️⃣ اطلاعات مرورگر:', {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    online: navigator.onLine
});

console.log('🏁 تست تکمیل شد. نتایج را در بالا مشاهده کنید.');







