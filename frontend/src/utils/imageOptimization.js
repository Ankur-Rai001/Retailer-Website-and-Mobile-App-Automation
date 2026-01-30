// Image optimization utilities for low-data usage

/**
 * Compress image URL by adding size and quality parameters
 * Works with Unsplash and common image CDNs
 */
export const optimizeImageUrl = (url, options = {}) => {
  const {
    width = 400,
    quality = 60,
    format = 'webp'
  } = options;

  if (!url) return '';

  try {
    const urlObj = new URL(url);
    
    // Unsplash optimization
    if (urlObj.hostname.includes('unsplash.com')) {
      urlObj.searchParams.set('w', width.toString());
      urlObj.searchParams.set('q', quality.toString());
      urlObj.searchParams.set('fm', format);
      urlObj.searchParams.set('auto', 'format');
      return urlObj.toString();
    }
    
    // Cloudinary optimization
    if (urlObj.hostname.includes('cloudinary.com')) {
      const parts = urlObj.pathname.split('/');
      const uploadIndex = parts.indexOf('upload');
      if (uploadIndex !== -1) {
        parts.splice(uploadIndex + 1, 0, `w_${width},q_${quality},f_${format}`);
        urlObj.pathname = parts.join('/');
        return urlObj.toString();
      }
    }
    
    // For other URLs, return as-is (could be enhanced for other CDNs)
    return url;
  } catch (error) {
    console.error('Image URL optimization failed:', error);
    return url;
  }
};

/**
 * Get appropriate image size based on device and network
 */
export const getOptimalImageSize = () => {
  // Check connection type (if available)
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  
  if (connection) {
    const effectiveType = connection.effectiveType;
    
    // Slow connection (2G, slow-2g)
    if (effectiveType === 'slow-2g' || effectiveType === '2g') {
      return { width: 200, quality: 40 };
    }
    
    // Medium connection (3G)
    if (effectiveType === '3g') {
      return { width: 400, quality: 60 };
    }
  }
  
  // Check device pixel ratio
  const dpr = window.devicePixelRatio || 1;
  
  // Mobile devices
  if (window.innerWidth < 768) {
    return { width: Math.round(400 * dpr), quality: 70 };
  }
  
  // Desktop
  return { width: Math.round(800 * dpr), quality: 80 };
};

/**
 * Lazy load images with IntersectionObserver
 */
export const lazyLoadImages = () => {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          const src = img.getAttribute('data-src');
          
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
          }
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    });
    
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => imageObserver.observe(img));
    
    return imageObserver;
  }
};

/**
 * Convert image to WebP if supported
 */
export const supportsWebP = () => {
  const canvas = document.createElement('canvas');
  if (canvas.getContext && canvas.getContext('2d')) {
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }
  return false;
};

/**
 * Get data saver mode status
 */
export const isDataSaverMode = () => {
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  return connection && connection.saveData === true;
};

/**
 * Preload critical images
 */
export const preloadImage = (url) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
};

/**
 * Get responsive image srcset
 */
export const getResponsiveSrcSet = (baseUrl) => {
  const sizes = [320, 640, 960, 1280];
  return sizes
    .map(width => `${optimizeImageUrl(baseUrl, { width })} ${width}w`)
    .join(', ');
};
