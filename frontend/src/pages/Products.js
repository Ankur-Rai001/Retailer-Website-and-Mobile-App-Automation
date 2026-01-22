import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Package, Plus, Edit, Trash2, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Products() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category: '',
    images: []
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`, { withCredentials: true });
      setProducts(response.data);
    } catch (error) {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      ...formData,
      price: parseFloat(formData.price),
      stock: parseInt(formData.stock)
    };

    try {
      if (editingProduct) {
        await axios.patch(`${API}/products/${editingProduct.product_id}`, payload, { withCredentials: true });
        toast.success('Product updated successfully');
      } else {
        await axios.post(`${API}/products`, payload, { withCredentials: true });
        toast.success('Product added successfully');
      }
      
      setShowAddDialog(false);
      setEditingProduct(null);
      setFormData({ name: '', description: '', price: '', stock: '', category: '', images: [] });
      fetchProducts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      description: product.description || '',
      price: product.price.toString(),
      stock: product.stock.toString(),
      category: product.category || '',
      images: product.images || []
    });
    setShowAddDialog(true);
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await axios.delete(`${API}/products/${productId}`, { withCredentials: true });
      toast.success('Product deleted');
      fetchProducts();
    } catch (error) {
      toast.error('Failed to delete product');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/dashboard')}
                data-testid="back-button"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <h1 className="text-2xl font-bold text-secondary">Products</h1>
            </div>
            <Button 
              onClick={() => {
                setEditingProduct(null);
                setFormData({ name: '', description: '', price: '', stock: '', category: '', images: [] });
                setShowAddDialog(true);
              }}
              data-testid="add-product-btn"
              className="bg-primary text-white hover:bg-primary/90 rounded-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Product
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {products.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
            <Package className="h-16 w-16 text-muted mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-secondary mb-2">No products yet</h3>
            <p className="text-muted mb-6">Start by adding your first product</p>
            <Button 
              onClick={() => setShowAddDialog(true)}
              className="bg-primary text-white hover:bg-primary/90 rounded-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Product
            </Button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <div key={product.product_id} className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-secondary mb-1">{product.name}</h3>
                    {product.description && (
                      <p className="text-sm text-muted line-clamp-2">{product.description}</p>
                    )}
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted">Price</span>
                    <span className="text-lg font-bold text-secondary">₹{product.price}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted">Stock</span>
                    <span className={`text-sm font-semibold ${product.stock > 10 ? 'text-accent' : product.stock > 0 ? 'text-orange-500' : 'text-red-500'}`}>
                      {product.stock} units
                    </span>
                  </div>
                  {product.category && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted">Category</span>
                      <span className="text-sm font-medium text-secondary capitalize">{product.category}</span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button 
                    onClick={() => handleEdit(product)}
                    variant="outline"
                    size="sm"
                    className="flex-1"
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button 
                    onClick={() => handleDelete(product.product_id)}
                    variant="destructive"
                    size="sm"
                    className="flex-1"
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingProduct ? 'Edit Product' : 'Add New Product'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Product Name *</Label>
              <Input
                id="name"
                data-testid="product-name-input"
                placeholder="e.g., Tata Salt 1kg"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="h-12"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                data-testid="product-description-input"
                placeholder="Product description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="h-12"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="price">Price (₹) *</Label>
                <Input
                  id="price"
                  data-testid="product-price-input"
                  type="number"
                  step="0.01"
                  placeholder="99.00"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  className="h-12"
                  required
                />
              </div>
              <div>
                <Label htmlFor="stock">Stock Quantity *</Label>
                <Input
                  id="stock"
                  data-testid="product-stock-input"
                  type="number"
                  placeholder="100"
                  value={formData.stock}
                  onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                  className="h-12"
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                data-testid="product-category-input"
                placeholder="e.g., Groceries, Snacks"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="h-12"
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowAddDialog(false);
                  setEditingProduct(null);
                  setFormData({ name: '', description: '', price: '', stock: '', category: '', images: [] });
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                data-testid="save-product-button"
                className="flex-1 bg-primary text-white hover:bg-primary/90"
              >
                {editingProduct ? 'Update Product' : 'Add Product'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
