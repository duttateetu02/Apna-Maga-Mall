from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "mega_mall_ultra_key"

# --- INVENTORY ---
inventory = {
    "Aashirvaad Atta (10kg)": 520, "Fortune Oil (5L)": 750, "Basmati Rice (5kg)": 480, 
    "Toor Dal (1kg)": 145, "Smartphone (Entry Level)": 8999, "Bluetooth Earbuds": 1499,
    "Cotton T-Shirt": 499, "Denim Jeans": 1299, "Electric Kettle": 999
}

sales_history = []

# --- 1. MAIN PAGE (Yahan sabse zyada galti hoti hai) ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'cart' not in session:
        session['cart'] = []
    
    message = ""
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Saman Bag mein daalne ke liye
        if action == 'add':
            item_name = request.form.get('item')
            quantity = int(request.form.get('quantity', 1))
            price = inventory.get(item_name)
            
            if price:
                cart = session.get('cart', [])
                cart.append({'name': item_name, 'qty': quantity, 'price': price * quantity})
                session['cart'] = cart
                message = f"✅ {item_name} added to Bag!"

    grand_total = sum(i['price'] for i in session['cart'])
    discount = (grand_total * 0.15) if grand_total >= 2000 else 0
    
    # Ye line HTML ko sari jankari bhejti hai
    return render_template_string(HTML_TEMPLATE, inventory=dict(sorted(inventory.items())), cart=session['cart'], total=grand_total, disc=discount, msg=message)

# --- 2. CHECKOUT (Summary aur Time fix yahan hai) ---
@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if cart:
        # INDIAN TIME FIX (+5:30)
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        formatted_time = ist_time.strftime("%I:%M %p") 
        
        # SUMMARY FIX (Ab technical naam nahi, asali naam aayenge)
        items_summary = ", ".join([f"{i['name']}(x{i['qty']})" for i in cart])
        
        final_total = sum(i['price'] for i in cart)
        discount = (final_total * 0.15) if final_total >= 2000 else 0
        amount_paid = final_total - discount

        sales_history.append({
            'time': formatted_time,
            'items': items_summary,
            'total': round(amount_paid, 2)
        })
        
        session.pop('cart', None)
        # Order hone ke baad ek sunder message dikhayega
        return f"<div style='text-align:center;padding:100px;font-family:sans-serif;'><h1>🛍️ Order Success!</h1><p>Items: {items_summary}</p><br><a href='/' style='padding:10px 20px; background:green; color:white; text-decoration:none; border-radius:5px;'>Wapas Jayein</a></div>"
    return redirect('/')

# --- 3. ADMIN PAGE ---
@app.route('/admin')
def admin():
    total_rev = sum(sale['total'] for sale in sales_history)
    return render_template_string(ADMIN_TEMPLATE, inventory=inventory, history=sales_history, revenue=total_rev)

# --- DESIGN (HTML) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mega Mall 2026</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .grid-container { height: 70vh; overflow-y: scroll; padding: 15px; background: #fff; border-radius: 15px; }
        .item-card { border: 1px solid #eee; padding: 15px; border-radius: 12px; margin-bottom: 15px; transition: 0.3s; }
        .item-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary shadow-sm mb-4"><div class="container"><h3>🏙️ MEGA MALL 2026</h3><a href="/admin" class="btn btn-warning fw-bold">Admin Dashboard</a></div></nav>
    <div class="container">
        {% if msg %}<div class="alert alert-success alert-dismissible fade show">{{msg}}</div>{% endif %}
        <div class="row">
            <div class="col-md-8">
                <div class="grid-container shadow-sm">
                    <div class="row">
                        {% for item, price in inventory.items() %}
                        <div class="col-md-4">
                            <div class="item-card text-center bg-white">
                                <h6 class="text-secondary">{{item}}</h6>
                                <h4 class="text-primary">Rs {{price}}</h4>
                                <form method="POST">
                                    <input type="hidden" name="action" value="add">
                                    <input type="hidden" name="item" value="{{item}}">
                                    <input type="number" name="quantity" value="1" min="1" class="form-control form-control-sm mb-2 mx-auto" style="width: 60px;">
                                    <button class="btn btn-sm btn-success w-100">Add to Bag</button>
                                </form>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card shadow border-0 p-3">
                    <h5 class="border-bottom pb-2">🛒 Your Shopping Bag</h5>
                    <div style="max-height: 250px; overflow-y: auto;">
                        <table class="table table-sm small">
                            {% for i in cart %}
                            <tr><td>{{i.name}}</td><td>x{{i.qty}}</td><td class="text-end">Rs {{i.price}}</td></tr>
                            {% endfor %}
                        </table>
                    </div>
                    <div class="bg-dark text-white p-3 rounded">
                        <div class="d-flex justify-content-between small"><span>Subtotal:</span><span>Rs {{total}}</span></div>
                        <div class="d-flex justify-content-between text-warning small"><span>Discount (15%):</span><span>- Rs {{disc}}</span></div>
                        <hr>
                        <h4 class="text-center mb-0">Total: Rs {{total - disc}}</h4>
                    </div>
                    <form action="/checkout" method="POST" class="mt-3">
                        <button class="btn btn-danger btn-lg w-100 shadow">PLACE ORDER</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<div style="font-family: sans-serif; padding: 40px; max-width: 900px; margin: auto;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1>📊 Sales Analysis</h1>
        <a href="/" style="text-decoration: none; color: blue;">← Back to Mall</a>
    </div>
    <div style="background: #e9f7ef; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: #27ae60; margin: 0;">Total Revenue: Rs {{revenue}}</h2>
    </div>
    <h3>Recent Orders</h3>
    <table border="1" width="100%" cellpadding="12" style="border-collapse: collapse; border: 1px solid #ddd;">
        <thead style="background: #f8f9fa;">
            <tr><th>Time (IST)</th><th>Order Summary</th><th>Amount Paid</th></tr>
        </thead>
        <tbody>
            {% for sale in history %}
            <tr>
                <td>{{sale.time}}</td>
                <td style="color: #555;">{{sale.items}}</td>
                <td style="font-weight: bold;">Rs {{sale.total}}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
'''

if __name__ == '__main__':
    app.run(debug=True)