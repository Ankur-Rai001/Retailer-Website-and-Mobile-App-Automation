// IndexedDB wrapper for offline storage
const DB_NAME = 'shopswift_db';
const DB_VERSION = 1;

class OfflineStorage {
  constructor() {
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object stores
        if (!db.objectStoreNames.contains('products')) {
          const productStore = db.createObjectStore('products', { keyPath: 'product_id' });
          productStore.createIndex('store_id', 'store_id', { unique: false });
          productStore.createIndex('category', 'category', { unique: false });
        }

        if (!db.objectStoreNames.contains('orders')) {
          const orderStore = db.createObjectStore('orders', { keyPath: 'order_id' });
          orderStore.createIndex('store_id', 'store_id', { unique: false });
          orderStore.createIndex('status', 'status', { unique: false });
        }

        if (!db.objectStoreNames.contains('store')) {
          db.createObjectStore('store', { keyPath: 'store_id' });
        }

        if (!db.objectStoreNames.contains('pendingSync')) {
          db.createObjectStore('pendingSync', { keyPath: 'id', autoIncrement: true });
        }
      };
    });
  }

  async saveProducts(products) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('products', 'readwrite');
    const store = tx.objectStore('products');
    
    for (const product of products) {
      await store.put(product);
    }
    
    return tx.complete;
  }

  async getProducts(storeId) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('products', 'readonly');
    const store = tx.objectStore('products');
    const index = store.index('store_id');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(storeId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async saveOrders(orders) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('orders', 'readwrite');
    const store = tx.objectStore('orders');
    
    for (const order of orders) {
      await store.put(order);
    }
    
    return tx.complete;
  }

  async getOrders(storeId) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('orders', 'readonly');
    const store = tx.objectStore('orders');
    const index = store.index('store_id');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(storeId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async saveStore(storeData) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('store', 'readwrite');
    const store = tx.objectStore('store');
    await store.put(storeData);
    return tx.complete;
  }

  async getStore(storeId) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('store', 'readonly');
    const store = tx.objectStore('store');
    
    return new Promise((resolve, reject) => {
      const request = store.get(storeId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async addPendingSync(action, data) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('pendingSync', 'readwrite');
    const store = tx.objectStore('pendingSync');
    await store.add({
      action,
      data,
      timestamp: Date.now()
    });
    return tx.complete;
  }

  async getPendingSync() {
    if (!this.db) await this.init();
    const tx = this.db.transaction('pendingSync', 'readonly');
    const store = tx.objectStore('pendingSync');
    
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async clearPendingSync(id) {
    if (!this.db) await this.init();
    const tx = this.db.transaction('pendingSync', 'readwrite');
    const store = tx.objectStore('pendingSync');
    await store.delete(id);
    return tx.complete;
  }

  async clearAll() {
    if (!this.db) await this.init();
    const stores = ['products', 'orders', 'store', 'pendingSync'];
    
    for (const storeName of stores) {
      const tx = this.db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      await store.clear();
    }
  }
}

export const offlineStorage = new OfflineStorage();
