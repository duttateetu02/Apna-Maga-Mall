from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mega_mall_ultra_key"

# --- 150+ ITEM MEGA INVENTORY ---
inventory = {
    # --- GROCERIES & KITCHEN ---
    "Aashirvaad Atta (10kg)": 520, "Fortune Oil (5L)": 750, "Basmati Rice (5kg)": 480, 
    "Toor Dal (1kg)": 145, "Sugar (5kg)": 230, "Tata Salt (1kg)": 28, "Maggi Family Pack": 96,
    "Honey (500g)": 199, "Olive Oil (1L)": 950, "Coffee (200g)": 350, "Tea Powder (1kg)": 420,

    # --- DAIRY & FROZEN ---
    "Amul Milk (1L)": 66, "Cheese Block (500g)": 350, "Frozen Peas (1kg)": 120,
    "Ice Cream Party Pack": 250, "Greek Yogurt": 50, "Butter (500g)": 255,

    # --- ELECTRONICS & GADGETS ---
    "Smartphone (Entry Level)": 8999, "Bluetooth Earbuds": 1499, "Power Bank 10k mAh": 999,
    "Smart Watch": 2499, "Laptop Backpack": 1200, "USB-C Cable": 299, "Wireless Mouse": 499,
    "LED Bulb (12W)": 120, "Trimmer": 1100, "Hair Dryer": 850,

    # --- FASHION & CLOTHING ---
    "Cotton T-Shirt": 499, "Denim Jeans": 1299, "Formal Shirt": 899, "Running Shoes": 1999,
    "Socks (Pair of 3)": 250, "Leather Belt": 550, "Sunglasses": 799, "Flip Flops": 299,

    # --- HOME & KITCHEN APPLIANCES ---
    "Electric Kettle": 999, "Sandwich Maker": 1250, "Hand Blender": 1100, "Iron Box": 750,
    "Dinner Set (12 pcs)": 1500, "Non-Stick Pan": 650, "Water Bottle (Steel)": 350,

    # --- PERSONAL CARE ---
    "Shampoo (400ml)": 350, "Conditioner": 280, "Perfume (Premium)": 1200, "Sunscreen": 450,
    "Body Wash": 250, "Face Cream": 200, "Electric Toothbrush": 1800,

    # --- TOYS & STATIONERY ---
    "Remote Control Car": 1200, "Building Blocks Set": 850, "Cricket Bat": 1500,
    "Football": 650, "Premium Pen Set": 450, "Drawing Kit": 300, "Calculator": 550
}

# (Baki bache 100+ items ki list ko bhi aap is tarah expand kar sakte hain)

sales_history = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'cart' not in session: session['cart'] = []
    message = ""
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            item = request.form.get('item')
            qty = int(request.form.get('quantity', 1))
            if item in inventory:
                session['cart'].append({'name': item, 'qty': qty, 'price': inventory[item] * qty})
                session.modified = True
                message = f"✅ {item} Added!"
        elif action == 'checkout':
            if session['cart']:
                total = sum(i['price'] for i in session['cart'])
                # BADA MALL = BADA DISCOUNT: 2000 se upar 15% Off
                disc = (total * 0.15) if total >= 2000 else 0
                sales_history.append({'time': datetime.now().strftime("%H:%M"), 'items': f"{len(session['cart'])} Items", 'total': total - disc})
                session.pop('cart', None)
                return f"<div style='text-align:center;padding:100px;'><h1>🛍️ Thank you for Shopping!</h1><h3>Paid: Rs {total-disc}</h3><a href='/'>Shop Again</a></div>"
        elif action == 'clear':
            session.pop('cart', None)
            return redirect('/')

    grand_total = sum(i['price'] for i in session['cart'])
    discount = (grand_total * 0.15) if grand_total >= 2000 else 0
    
    return render_template_string(HTML_TEMPLATE, inventory=dict(sorted(inventory.items())), cart=session['cart'], total=grand_total, disc=discount, msg=message)

@app.route('/admin')
def admin():
    total_rev = sum(sale['total'] for sale in sales_history)
    return render_template_string(ADMIN_TEMPLATE, inventory=inventory, history=sales_history, revenue=total_rev)

# --- DESIGN (SCROLLABLE UI) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .grid-container { height: 75vh; overflow-y: scroll; padding: 10px; border: 1px solid #ddd; border-radius: 10px; background: white; }
        .item-card { border: 1px solid #eee; padding: 10px; border-radius: 8px; margin-bottom: 10px; background: #fafafa; }
        .item-card:hover { background: #e9f7ef; border-color: #28a745; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary shadow mb-4"><div class="container"><h3>🏙️ MEGA MALL 2026</h3><a href="/admin" class="btn btn-warning">Mall Dashboard</a></div></nav>
    <div class="container-fluid px-5">
        <div class="row">
            <div class="col-md-8">
                <div class="grid-container shadow-sm">
                    <div class="row">
                        {% for item, price in inventory.items() %}
                        <div class="col-md-4">
                            <div class="item-card shadow-sm text-center">
                                <h6 class="text-truncate">{{item}}</h6>
                                <h5 class="text-primary">Rs {{price}}</h5>
                                <form method="POST">
                                    <input type="hidden" name="action" value="add"><input type="hidden" name="item" value="{{item}}">
                                    <div class="input-group input-group-sm mb-2"><input type="number" name="quantity" value="1" min="1" class="form-control"></div>
                                    <button class="btn btn-sm btn-outline-success w-100">Add to Bag</button>
                                </form>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3 shadow border-0">
                    <h4 class="text-center">Your Shopping Bag</h4>
                    <hr>
                    <div style="max-height: 300px; overflow-y: auto;">
                        <table class="table table-sm small">
                            {% for i in cart %}<tr><td>{{i.name}}</td><td>x{{i.qty}}</td><td>Rs {{i.price}}</td></tr>{% endfor %}
                        </table>
                    </div>
                    <div class="bg-dark text-white p-3 rounded mt-2">
                        <div class="d-flex justify-content-between"><span>Subtotal:</span> <span>Rs {{total}}</span></div>
                        <div class="d-flex justify-content-between text-warning"><span>Discount (15%):</span> <span>- Rs {{disc}}</span></div>
                        <hr>
                        <h3 class="text-center">Total: Rs {{total - disc}}</h3>
                    </div>
                    <form method="POST" class="mt-3"><input type="hidden" name="action" value="checkout"><button class="btn btn-danger w-100 py-3">💳 PLACE ORDER</button></form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<div style="font-family: Arial; padding: 50px;">
    <h1>🏬 Mall Sales Analysis</h1>
    <h2 style="color: green;">Total Revenue: Rs {{revenue}}</h2>
    <hr>
    <h3>Recent Orders</h3>
    <table border="1" width="100%" cellpadding="10">
        <tr style="background: #eee;"><th>Time</th><th>Summary</th><th>Amount Paid</th></tr>
        {% for sale in history %}
        <tr><td>{{sale.time}}</td><td>{{sale.items}}</td><td>Rs {{sale.total}}</td></tr>
        {% endfor %}
    </table>
    <br><a href="/">Back to Mall</a>
</div>
'''

if __name__ == '__main__':
    app.run(debug=True)