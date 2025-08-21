export interface OilFilterInfo {
  id: string;
  name: string;
  address: string;
  phone: string;
}

export const oilFilterData: Record<string, Record<string, OilFilterInfo[]>> = {
  'تهران': {
    'تهران': [
      { id: '1', name: 'فروشگاه روغن پارس', address: 'تهران، خیابان انقلاب', phone: '021-11111111' },
      { id: '2', name: 'فروشگاه فیلتر تهران', address: 'تهران، خیابان آزادی', phone: '021-22222222' },
    ],
    'شمیرانات': [
      { id: '3', name: 'روغن و فیلتر شمال', address: 'شمیرانات، خیابان دربند', phone: '021-33333333' },
    ],
  },
  'اصفهان': {
    'اصفهان': [
      { id: '4', name: 'روغن اصفهان', address: 'اصفهان، میدان نقش جهان', phone: '031-11111111' },
    ],
    'کاشان': [
      { id: '5', name: 'فروشگاه فیلتر کاشان', address: 'کاشان، خیابان ملاصدرا', phone: '031-22222222' },
    ],
  },
};

export default oilFilterData;
