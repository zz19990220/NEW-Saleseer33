#!/usr/bin/env python3

import os
import csv

# Create directory if it doesn't exist
os.makedirs('inventory/sample_data', exist_ok=True)

# Define the product data
products = [
    ['Red Sneakers', 'shoes', 'red', '119.99', '4.5', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff'],
    ['Blue Jeans', 'jeans', 'blue', '89.99', '4.2', 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246'],
    ['Black Leather Jacket', 'jacket', 'black', '249.99', '4.8', 'https://images.unsplash.com/photo-1551028719-00167b16eac5'],
    ['White Cotton T-shirt', 'tshirt', 'white', '24.99', '4.0', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab'],
    ['Red Summer Dress', 'dress', 'red', '149.99', '4.7', 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1'],
    ['Navy Blazer', 'blazer', 'blue', '179.99', '4.3', 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35'],
    ['Brown Leather Boots', 'shoes', 'brown', '199.99', '4.6', 'https://images.unsplash.com/photo-1542838687-307f8d662565'],
    ['Pink Blouse', 'blouse', 'pink', '59.99', '4.1', 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992'],
    ['Gray Wool Sweater', 'sweater', 'gray', '79.99', '4.4', 'https://images.unsplash.com/photo-1616677307289-6f0e87feea0e'],
    ['Black Running Shoes', 'shoes', 'black', '129.99', '4.7', 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3'],
    ['Green Hoodie', 'hoodie', 'green', '69.99', '4.2', 'https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77'],
    ['Beige Trench Coat', 'coat', 'beige', '229.99', '4.9', 'https://images.unsplash.com/photo-1591900947067-851789555ef3'],
    ['Blue Denim Shorts', 'shorts', 'blue', '49.99', '4.0', 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b'],
    ['Red High Heels', 'shoes', 'red', '159.99', '4.5', 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2'],
    ['Black Mini Skirt', 'skirt', 'black', '69.99', '4.2', 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa'],
    ['White Sneakers', 'shoes', 'white', '99.99', '4.6', 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3'],
    ['Blue Polo Shirt', 'tshirt', 'blue', '39.99', '4.1', 'https://images.unsplash.com/photo-1576566588028-4147f3842f27'],
    ['Red Cardigan', 'cardigan', 'red', '89.99', '4.3', 'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983'],
    ['Black Dress Pants', 'pants', 'black', '109.99', '4.5', 'https://images.unsplash.com/photo-1604176424472-0da33b933caa'],
    ['Cream Knit Scarf', 'accessory', 'beige', '29.99', '4.0', 'https://images.unsplash.com/photo-1620231175813-4ed738896bd9'],
    ['Gold Hoop Earrings', 'accessory', 'gold', '59.99', '4.7', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f'],
    ['Silver Necklace', 'accessory', 'silver', '79.99', '4.5', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f'],
    ['Blue Athletic Shorts', 'shorts', 'blue', '34.99', '4.2', 'https://images.unsplash.com/photo-1562087926-662d6fd7062d'],
    ['Gray Sweatpants', 'pants', 'gray', '49.99', '4.1', 'https://images.unsplash.com/photo-1580991984231-54fc501bb6dd'],
    ['Red Baseball Cap', 'accessory', 'red', '24.99', '4.0', 'https://images.unsplash.com/photo-1521369909029-2afed882baee'],
    ['Black Leather Bag', 'bag', 'black', '199.99', '4.8', 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d'],
    ['White Linen Shirt', 'shirt', 'white', '79.99', '4.3', 'https://images.unsplash.com/photo-1598032895397-b9472444bf93'],
    ['Brown Leather Belt', 'accessory', 'brown', '49.99', '4.4', 'https://images.unsplash.com/photo-1591639554383-1090312348f4'],
    ['Navy Swim Trunks', 'swimwear', 'blue', '39.99', '4.0', 'https://images.unsplash.com/photo-1545693315-85b6be26a3b5'],
    ['Black Sunglasses', 'accessory', 'black', '129.99', '4.6', 'https://images.unsplash.com/photo-1577803645773-f96470509666'],
    ['Denim Jacket', 'jacket', 'blue', '119.99', '4.4', 'https://images.unsplash.com/photo-1551537482-f2075a1d41f2'],
    ['Gray Beanie', 'accessory', 'gray', '19.99', '4.1', 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531'],
    ['Red Plaid Shirt', 'shirt', 'red', '59.99', '4.2', 'https://images.unsplash.com/photo-1608844082169-80b4a2a986ff'],
    ['Black Ankle Boots', 'shoes', 'black', '149.99', '4.7', 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2'],
    ['White Tennis Skirt', 'skirt', 'white', '49.99', '4.3', 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa'],
    ['Navy Peacoat', 'coat', 'blue', '279.99', '4.9', 'https://images.unsplash.com/photo-1591900947067-851789555ef3'],
    ['Pink Summer Hat', 'accessory', 'pink', '34.99', '4.2', 'https://images.unsplash.com/photo-1565839360674-fea973cbebe1'],
    ['Black Yoga Pants', 'pants', 'black', '69.99', '4.6', 'https://images.unsplash.com/photo-1580991984231-54fc501bb6dd'],
    ['Green Silk Scarf', 'accessory', 'green', '59.99', '4.4', 'https://images.unsplash.com/photo-1620231175813-4ed738896bd9'],
    ['Striped Beach Towel', 'accessory', 'blue', '19.99', '4.1', 'https://images.unsplash.com/photo-1587150003836-a9933a37473f']
]

# Write data to CSV file
with open('inventory/sample_data/sample_products.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'category', 'color', 'price', 'rating', 'image_url'])
    writer.writerows(products)

print("Sample product data has been created successfully!") 