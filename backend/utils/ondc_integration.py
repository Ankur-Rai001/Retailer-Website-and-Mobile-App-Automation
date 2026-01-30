# ONDC Integration for ShopSwift India Seller App
import os
import json
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import requests
import uuid

class ONDCIntegration:
    def __init__(self, subscriber_id: str, subscriber_url: str, signing_key: str):
        self.subscriber_id = subscriber_id  # Unique ID for ShopSwift seller
        self.subscriber_url = subscriber_url  # Webhook URL
        self.signing_key = signing_key  # For request signing
        self.ondc_staging_url = "https://staging.registry.ondc.org/ondc"
        self.beckn_version = "1.0.0"
        
    def create_beckn_context(self, action: str, domain: str = "nic2004:52110") -> Dict:
        """Create Beckn protocol context"""
        return {
            "domain": domain,  # Retail domain
            "country": "IND",
            "city": "*",  # All cities
            "action": action,
            "core_version": self.beckn_version,
            "bap_id": "buyer-app.ondc.org",  # Buyer app ID (example)
            "bap_uri": "https://buyer-app.ondc.org/protocol/v1",
            "bpp_id": self.subscriber_id,
            "bpp_uri": self.subscriber_url,
            "transaction_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ttl": "PT30S"
        }
    
    def sign_request(self, request_body: str) -> str:
        """Sign request using HMAC-SHA256"""
        signature = hmac.new(
            self.signing_key.encode(),
            request_body.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def create_catalog_payload(self, store_data: Dict, products: List[Dict]) -> Dict:
        """Create ONDC catalog payload from store and products"""
        
        # Create provider (store) object
        provider = {
            "id": store_data["store_id"],
            "descriptor": {
                "name": store_data["store_name"],
                "short_desc": store_data.get("description", "")[:100],
                "long_desc": store_data.get("description", ""),
                "images": [
                    {"url": store_data.get("logo_url", "")} if store_data.get("logo_url") else {}
                ]
            },
            "locations": [
                {
                    "id": f"{store_data['store_id']}_loc1",
                    "gps": "28.5355,77.3910",  # Default coords, should be actual
                    "address": {
                        "street": store_data.get("address", ""),
                        "city": "Delhi",
                        "state": "Delhi",
                        "country": "IND",
                        "area_code": "110001"
                    }
                }
            ],
            "categories": [
                {
                    "id": store_data.get("category", "grocery"),
                    "descriptor": {"name": store_data.get("category", "grocery").title()}
                }
            ],
            "items": self._convert_products_to_ondc_items(products, store_data["store_id"])
        }
        
        return provider
    
    def _convert_products_to_ondc_items(self, products: List[Dict], store_id: str) -> List[Dict]:
        """Convert ShopSwift products to ONDC item format"""
        items = []
        
        for product in products:
            item = {
                "id": product["product_id"],
                "descriptor": {
                    "name": product["name"],
                    "short_desc": product.get("description", "")[:100] if product.get("description") else "",
                    "long_desc": product.get("description", ""),
                    "images": [{"url": img} for img in product.get("images", [])[:3]]
                },
                "price": {
                    "currency": "INR",
                    "value": str(product["price"]),
                    "maximum_value": str(product["price"])
                },
                "quantity": {
                    "available": {
                        "count": str(product["stock"])
                    },
                    "maximum": {
                        "count": "99"
                    }
                },
                "category_id": product.get("category", "grocery"),
                "location_id": f"{store_id}_loc1",
                "@ondc/org/returnable": True,
                "@ondc/org/cancellable": True,
                "@ondc/org/return_window": "P7D",
                "@ondc/org/seller_pickup_return": True,
                "@ondc/org/time_to_ship": "PT2H",
                "@ondc/org/available_on_cod": True,
                "tags": [
                    {
                        "code": "origin",
                        "list": [{"code": "country", "value": "IND"}]
                    }
                ]
            }
            items.append(item)
        
        return items
    
    def sync_catalog_to_ondc(self, store_data: Dict, products: List[Dict]) -> Dict:
        """Sync catalog to ONDC network"""
        try:
            context = self.create_beckn_context("on_search")
            provider = self.create_catalog_payload(store_data, products)
            
            payload = {
                "context": context,
                "message": {
                    "catalog": {
                        "bpp/descriptor": {
                            "name": "ShopSwift India",
                            "short_desc": "Digital commerce platform for retailers",
                            "long_desc": "ShopSwift India enables small retailers to sell online",
                            "images": [{"url": "https://shopswift.in/logo.png"}]
                        },
                        "bpp/providers": [provider]
                    }
                }
            }
            
            return {"success": True, "payload": payload, "message": "Catalog ready for ONDC"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_search_request(self, search_payload: Dict) -> Dict:
        """Handle incoming search request from ONDC buyer apps"""
        context = search_payload.get("context", {})
        message = search_payload.get("message", {})
        intent = message.get("intent", {})
        
        # Extract search parameters
        search_string = intent.get("item", {}).get("descriptor", {}).get("name", "")
        category = intent.get("category", {}).get("id", "")
        
        return {
            "search_string": search_string,
            "category": category,
            "location": intent.get("fulfillment", {}).get("end", {}).get("location", {})
        }
    
    def create_select_response(self, order_items: List[Dict], store_data: Dict) -> Dict:
        """Create response for /select (item selection)"""
        context = self.create_beckn_context("on_select")
        
        quote = self._calculate_quote(order_items)
        
        return {
            "context": context,
            "message": {
                "order": {
                    "provider": {
                        "id": store_data["store_id"],
                        "locations": [{"id": f"{store_data['store_id']}_loc1"}]
                    },
                    "items": order_items,
                    "quote": quote,
                    "fulfillment": {
                        "type": "Delivery",
                        "tracking": False,
                        "@ondc/org/TAT": "PT2H",
                        "@ondc/org/category": "Standard Delivery"
                    }
                }
            }
        }
    
    def _calculate_quote(self, items: List[Dict]) -> Dict:
        """Calculate order quote with breakup"""
        total_price = sum(float(item.get("price", {}).get("value", 0)) * int(item.get("quantity", {}).get("count", 1)) for item in items)
        
        return {
            "price": {
                "currency": "INR",
                "value": str(total_price)
            },
            "breakup": [
                {
                    "title": "Base Price",
                    "price": {"currency": "INR", "value": str(total_price)}
                },
                {
                    "title": "Delivery Charges",
                    "price": {"currency": "INR", "value": "0"}
                }
            ]
        }
    
    def create_init_response(self, order_data: Dict, billing_info: Dict) -> Dict:
        """Create response for /init (order initialization)"""
        context = self.create_beckn_context("on_init")
        
        return {
            "context": context,
            "message": {
                "order": {
                    **order_data,
                    "billing": billing_info,
                    "payment": {
                        "type": "ON-ORDER",
                        "collected_by": "BAP",
                        "@ondc/org/buyer_app_finder_fee_type": "percent",
                        "@ondc/org/buyer_app_finder_fee_amount": "3",
                        "@ondc/org/settlement_details": [
                            {
                                "settlement_counterparty": "seller-app",
                                "settlement_type": "upi",
                                "upi_address": "shopswift@paytm",
                                "settlement_bank_account_no": "XXXXXXXXXX",
                                "settlement_ifsc_code": "XXXXXX"
                            }
                        ]
                    }
                }
            }
        }
    
    def create_confirm_response(self, order_id: str, order_data: Dict) -> Dict:
        """Create response for /confirm (order confirmation)"""
        context = self.create_beckn_context("on_confirm")
        
        return {
            "context": context,
            "message": {
                "order": {
                    "id": order_id,
                    "state": "Accepted",
                    "provider": order_data.get("provider"),
                    "items": order_data.get("items"),
                    "billing": order_data.get("billing"),
                    "fulfillment": {
                        "id": str(uuid.uuid4()),
                        "type": "Delivery",
                        "state": {"descriptor": {"code": "Pending"}},
                        "tracking": False,
                        "@ondc/org/TAT": "PT2H"
                    },
                    "quote": order_data.get("quote"),
                    "payment": order_data.get("payment"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    
    def update_order_status(self, order_id: str, status: str) -> Dict:
        """Send order status update to ONDC"""
        context = self.create_beckn_context("on_status")
        
        status_map = {
            "pending": "Pending",
            "processing": "In-progress",
            "completed": "Completed",
            "cancelled": "Cancelled"
        }
        
        return {
            "context": context,
            "message": {
                "order": {
                    "id": order_id,
                    "state": status_map.get(status, "Pending"),
                    "fulfillment": {
                        "state": {
                            "descriptor": {"code": status_map.get(status, "Pending")}
                        }
                    },
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
