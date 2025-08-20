export interface City {
  name: string;
  counties: string[];
}

export const cities: City[] = [
  {
    name: 'تهران',
    counties: ['تهران', 'کرج', 'شهریار', 'ورامین']
  },
  {
    name: 'اصفهان',
    counties: ['اصفهان']
  },
  {
    name: 'تبریز',
    counties: ['تبریز']
  }
];
