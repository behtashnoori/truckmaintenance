/**
 * Utility functions for Persian number conversion
 */

/**
 * Convert English numbers to Persian numbers
 * @param text - Text containing English numbers
 * @returns Text with Persian numbers
 */
export const convertToPersianNumbers = (text: string): string => {
  if (!text) return text;
  
  const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
  
  let result = text;
  for (let i = 0; i < englishNumbers.length; i++) {
    const regex = new RegExp(englishNumbers[i], 'g');
    result = result.replace(regex, persianNumbers[i]);
  }
  return result;
};

/**
 * Convert Persian numbers to English numbers
 * @param text - Text containing Persian numbers
 * @returns Text with English numbers
 */
export const convertToEnglishNumbers = (text: string): string => {
  if (!text) return text;
  
  const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
  
  let result = text;
  for (let i = 0; i < persianNumbers.length; i++) {
    const regex = new RegExp(persianNumbers[i], 'g');
    result = result.replace(regex, englishNumbers[i]);
  }
  return result;
};

/**
 * Check if a string contains numbers
 * @param text - Text to check
 * @returns True if text contains numbers
 */
export const containsNumbers = (text: string): boolean => {
  return /\d/.test(text);
};

/**
 * Format phone number to Persian format
 * @param phone - Phone number string
 * @returns Formatted Persian phone number
 */
export const formatPersianPhone = (phone: string): string => {
  // Remove all non-digit characters
  const digits = phone.replace(/\D/g, '');
  
  // Convert to Persian
  const persianDigits = convertToPersianNumbers(digits);
  
  // Format as Iranian phone number (if it's a valid length)
  if (digits.length === 11 && digits.startsWith('09')) {
    return `${persianDigits.slice(0, 4)}-${persianDigits.slice(4, 7)}-${persianDigits.slice(7)}`;
  } else if (digits.length === 11 && digits.startsWith('021')) {
    return `${persianDigits.slice(0, 3)}-${persianDigits.slice(3)}`;
  }
  
  return persianDigits;
};
