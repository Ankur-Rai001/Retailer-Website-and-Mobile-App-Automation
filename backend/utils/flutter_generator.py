# Flutter mobile app generation utilities
import os
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Any

class FlutterAppGenerator:
    def __init__(self, store_data: Dict[str, Any]):
        self.store_data = store_data
        self.store_id = store_data['store_id']
        self.store_name = store_data['store_name']
        self.subdomain = store_data['subdomain']
        self.package_name = f"com.shopswift.{self.subdomain.lower().replace('-', '').replace('_', '')}"
        self.app_name = store_data['store_name'].replace(" ", "")
        
    def generate_pubspec_yaml(self) -> str:
        return f"""name: {self.app_name.lower()}
description: {self.store_data.get('description', 'Your online store app')}

publish_to: 'none'

version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  http: ^1.1.0
  shared_preferences: ^2.2.2
  cached_network_image: ^3.3.0
  url_launcher: ^6.2.1
  flutter_svg: ^2.0.9
  provider: ^6.1.1
  intl: ^0.18.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/
"""

    def generate_main_dart(self) -> str:
        api_url = f"https://{self.subdomain}.shopswift.in/api"
        return f"""import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/products_screen.dart';
import 'screens/product_detail_screen.dart';
import 'screens/cart_screen.dart';
import 'providers/store_provider.dart';

void main() {{
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => StoreProvider()),
      ],
      child: MyApp(),
    ),
  );
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{self.store_name}',
      theme: ThemeData(
        primarySwatch: Colors.orange,
        primaryColor: Color(0xFFF97316),
        scaffoldBackgroundColor: Color(0xFFF8FAFC),
        fontFamily: 'Manrope',
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.white,
          elevation: 0,
          iconTheme: IconThemeData(color: Color(0xFF0F172A)),
          titleTextStyle: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      home: HomeScreen(),
      routes: {{
        '/products': (context) => ProductsScreen(),
        '/cart': (context) => CartScreen(),
      }},
    );
  }}
}}
"""

    def generate_home_screen(self) -> str:
        return f"""import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/store_provider.dart';
import 'products_screen.dart';

class HomeScreen extends StatefulWidget {{
  @override
  _HomeScreenState createState() => _HomeScreenState();
}}

class _HomeScreenState extends State<HomeScreen> {{
  @override
  void initState() {{
    super.initState();
    Future.microtask(
      () => Provider.of<StoreProvider>(context, listen: false).loadStoreData(),
    );
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text('{self.store_name}'),
        actions: [
          IconButton(
            icon: Icon(Icons.shopping_cart),
            onPressed: () => Navigator.pushNamed(context, '/cart'),
          ),
        ],
      ),
      body: Consumer<StoreProvider>(
        builder: (context, storeProvider, child) {{
          if (storeProvider.isLoading) {{
            return Center(child: CircularProgressIndicator());
          }}

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Hero Banner
                Container(
                  width: double.infinity,
                  height: 200,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFFF97316), Color(0xFFFB923C)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Welcome to',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        '{self.store_name}',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        storeProvider.storeDescription ?? 'Your trusted online store',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),

                // Quick Actions
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Shop by Category',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                ),

                // Featured Products Button
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: ElevatedButton(
                    onPressed: () {{
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ProductsScreen()),
                      );
                    }},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color(0xFFF97316),
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.shopping_bag),
                        SizedBox(width: 8),
                        Text(
                          'Browse All Products',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                SizedBox(height: 24),

                // Store Info
                if (storeProvider.storePhone != null)
                  ListTile(
                    leading: Icon(Icons.phone, color: Color(0xFFF97316)),
                    title: Text('Contact Us'),
                    subtitle: Text(storeProvider.storePhone ?? ''),
                  ),

                if (storeProvider.storeAddress != null)
                  ListTile(
                    leading: Icon(Icons.location_on, color: Color(0xFFF97316)),
                    title: Text('Visit Us'),
                    subtitle: Text(storeProvider.storeAddress ?? ''),
                  ),
              ],
            ),
          );
        }},
      ),
    );
  }}
}}
"""

    def generate_products_screen(self) -> str:
        return """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../providers/store_provider.dart';
import '../models/product.dart';
import 'product_detail_screen.dart';

class ProductsScreen extends StatefulWidget {
  @override
  _ProductsScreenState createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => Provider.of<StoreProvider>(context, listen: false).loadProducts(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Products'),
        actions: [
          IconButton(
            icon: Icon(Icons.shopping_cart),
            onPressed: () => Navigator.pushNamed(context, '/cart'),
          ),
        ],
      ),
      body: Consumer<StoreProvider>(
        builder: (context, storeProvider, child) {
          if (storeProvider.isLoading) {
            return Center(child: CircularProgressIndicator());
          }

          if (storeProvider.products.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inventory_2_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No products available',
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return GridView.builder(
            padding: EdgeInsets.all(16),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.7,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: storeProvider.products.length,
            itemBuilder: (context, index) {
              final product = storeProvider.products[index];
              return ProductCard(product: product);
            },
          );
        },
      ),
    );
  }
}

class ProductCard extends StatelessWidget {
  final Product product;

  const ProductCard({required this.product});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductDetailScreen(product: product),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product Image
            ClipRRect(
              borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
              child: Container(
                height: 140,
                width: double.infinity,
                color: Color(0xFFF1F5F9),
                child: product.images.isNotEmpty
                    ? CachedNetworkImage(
                        imageUrl: product.images.first,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => Center(
                          child: CircularProgressIndicator(),
                        ),
                        errorWidget: (context, url, error) => Icon(
                          Icons.image_not_supported,
                          size: 48,
                          color: Colors.grey,
                        ),
                      )
                    : Icon(Icons.inventory_2, size: 48, color: Colors.grey),
              ),
            ),

            // Product Info
            Padding(
              padding: EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.name,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0F172A),
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 4),
                  Text(
                    '₹${product.price.toStringAsFixed(2)}',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFFF97316),
                    ),
                  ),
                  SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        product.stock > 0 ? Icons.check_circle : Icons.cancel,
                        size: 14,
                        color: product.stock > 0 ? Color(0xFF10B981) : Colors.red,
                      ),
                      SizedBox(width: 4),
                      Text(
                        product.stock > 0 ? 'In Stock' : 'Out of Stock',
                        style: TextStyle(
                          fontSize: 12,
                          color: product.stock > 0 ? Color(0xFF10B981) : Colors.red,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
"""

    def generate_store_provider(self) -> str:
        api_url = f"https://{self.subdomain}.shopswift.in/api"
        return f"""import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/product.dart';

class StoreProvider with ChangeNotifier {{
  bool _isLoading = false;
  List<Product> _products = [];
  String? _storeDescription;
  String? _storePhone;
  String? _storeAddress;

  bool get isLoading => _isLoading;
  List<Product> get products => _products;
  String? get storeDescription => _storeDescription;
  String? get storePhone => _storePhone;
  String? get storeAddress => _storeAddress;

  final String baseUrl = '{api_url}';

  Future<void> loadStoreData() async {{
    _isLoading = true;
    notifyListeners();

    try {{
      final response = await http.get(Uri.parse('$baseUrl/store-public/{self.store_id}'));
      
      if (response.statusCode == 200) {{
        final data = json.decode(response.body);
        _storeDescription = data['description'];
        _storePhone = data['phone'];
        _storeAddress = data['address'];
      }}
    }} catch (e) {{
      print('Error loading store data: $e');
    }} finally {{
      _isLoading = false;
      notifyListeners();
    }}
  }}

  Future<void> loadProducts() async {{
    _isLoading = true;
    notifyListeners();

    try {{
      final response = await http.get(Uri.parse('$baseUrl/products-public/{self.store_id}'));
      
      if (response.statusCode == 200) {{
        final List<dynamic> data = json.decode(response.body);
        _products = data.map((json) => Product.fromJson(json)).toList();
      }}
    }} catch (e) {{
      print('Error loading products: $e');
    }} finally {{
      _isLoading = false;
      notifyListeners();
    }}
  }}
}}
"""

    def generate_product_model(self) -> str:
        return """class Product {
  final String productId;
  final String name;
  final String? description;
  final double price;
  final int stock;
  final List<String> images;
  final String? category;
  final bool isActive;

  Product({
    required this.productId,
    required this.name,
    this.description,
    required this.price,
    required this.stock,
    required this.images,
    this.category,
    required this.isActive,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      productId: json['product_id'],
      name: json['name'],
      description: json['description'],
      price: json['price'].toDouble(),
      stock: json['stock'],
      images: List<String>.from(json['images'] ?? []),
      category: json['category'],
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'name': name,
      'description': description,
      'price': price,
      'stock': stock,
      'images': images,
      'category': category,
      'is_active': isActive,
    };
  }
}
"""

    def generate_android_manifest(self) -> str:
        return f"""<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{self.package_name}">
    
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>

    <application
        android:label="{self.store_name}"
        android:name="${{applicationName}}"
        android:icon="@mipmap/ic_launcher">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"
              />
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <meta-data
            android:name="flutterEmbedding"
            android:value="2" />
    </application>
</manifest>
"""

    def generate_build_gradle(self) -> str:
        return f"""android {{
    namespace "{self.package_name}"
    compileSdkVersion 34

    defaultConfig {{
        applicationId "{self.package_name}"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }}

    buildTypes {{
        release {{
            signingConfig signingConfigs.debug
            minifyEnabled true
            shrinkResources true
        }}
    }}
}}
"""

    def generate_readme(self) -> str:
        return f"""# {self.store_name} - Mobile App

Generated by ShopSwift India

## App Details
- **Store Name:** {self.store_name}
- **Package Name:** {self.package_name}
- **Store URL:** https://{self.subdomain}.shopswift.in

## Build Instructions

### Prerequisites
- Flutter SDK 3.0.0+
- Android Studio / Xcode
- Java JDK 17+

### Build APK (Android)
```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### Build IPA (iOS)
```bash
flutter build ios --release
```

## Publishing

See PUBLISHING_GUIDE.md for detailed instructions on publishing to Google Play and App Store.
"""

    def generate_all_files(self) -> Dict[str, str]:
        """Generate all Flutter project files"""
        return {
            'pubspec.yaml': self.generate_pubspec_yaml(),
            'lib/main.dart': self.generate_main_dart(),
            'lib/screens/home_screen.dart': self.generate_home_screen(),
            'lib/screens/products_screen.dart': self.generate_products_screen(),
            'lib/providers/store_provider.dart': self.generate_store_provider(),
            'lib/models/product.dart': self.generate_product_model(),
            'android/app/src/main/AndroidManifest.xml': self.generate_android_manifest(),
            'android/app/build.gradle': self.generate_build_gradle(),
            'README.md': self.generate_readme(),
        }
