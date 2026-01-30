export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date));
};

export const formatDateTime = (date) => {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
};

export const getStockStatus = (stock) => {
  if (stock === 0) return { text: 'Out of Stock', color: 'text-red-500' };
  if (stock <= 10) return { text: 'Low Stock', color: 'text-orange-500' };
  return { text: 'In Stock', color: 'text-accent' };
};

export const getOrderStatusColor = (status) => {
  const colors = {
    pending: 'bg-orange-100 text-orange-700',
    processing: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
  };
  return colors[status] || 'bg-gray-100 text-gray-700';
};

export const validateGST = (gstNumber) => {
  const gstRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
  return gstRegex.test(gstNumber);
};

export const validatePhone = (phone) => {
  const phoneRegex = /^[+]?[0-9]{10,15}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
};

export const generateSubdomain = (storeName) => {
  return storeName
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .substring(0, 20);
};
