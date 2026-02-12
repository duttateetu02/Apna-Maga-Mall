from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mega_mall_ultra_key"

# --- INVENTORY ---
inventory = {
    "Aashirvaad Atta (10kg)": 520, "Fortune Oil (5L)": 750, "Basmati Rice (5kg)": 480, 
    "Toor Dal (1kg)": 145, "Smartphone (Entry Level)": 8999, "Bluetooth Earbuds": 1499,
    "Cotton T-Shirt": 499, "Denim Jeans": 1299, "Electric Kettle": 999
}

sales_history = []

# --- 1. MAIN PAGE ROUTE (Ye missing tha) ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'cart' not in session:
        session['cart'] = []
    
    message = ""
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Add to Cart Logic
        if action == 'add':
            item_name = request.form.get('item')
            quantity = int(request.form.get('quantity', 1))
            price = inventory.get(item_name)
            
            if price:
                cart = session.get('cart', [])
                cart.append({'name': item_name, 'qty': quantity, 'price': price * quantity})
                session['cart'] = cart
                message = f"{item_name} added!"

        # Checkout Redirect
        elif action == 'checkout':
            return redirect(url_for('checkout'), code=307) # POST data ke saath checkout par bhej raha hai

    grand_total = sum(i['price'] for i in session['cart'])
    discount = (grand_total * 0.15) if grand_total >= 2000 else 0
    
    return render_template_string(HTML_TEMPLATE, inventory=dict(sorted(inventory.items())), cart=session['cart'], total=grand_total, disc=discount, msg=message)

# --- 2. CHECKOUT ROUTE ---
@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if cart:
        total = sum(i['price'] for i in cart)
        disc = (total * 0.15) if total >= 2000 else 0
        final = total - disc
        
        # SUMMARY FIX (Jo pehle built-in method dikha raha tha)
        items_summary = ", ".join([f"{i['name']}(x{i['qty']})" for i in cart])
        
        sales_history.append({
            'time': datetime.now().strftime("%H:%M"),
            'items': items_summary,
            'total': final
        })
        session.pop('cart', None)
        return f"<div style='text-align:center;padding:100px;'><h1>🛍️ Order Success!</h1><p>Items: {items_summary}</p><a href='/'>Wapas Jayein</a></div>"
    return redirect('/')

# --- 3. ADMIN ROUTE ---
@app.route('/admin')
def admin():
    total_rev = sum(sale['total'] for sale in sales_history)
    return render_template_string(ADMIN_TEMPLATE, inventory=inventory, history=sales_history, revenue=total_rev)

# --- DESIGN ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .grid-container { height: 75vh; overflow-y: scroll; padding: 10px; border: 1px solid #ddd; border-radius: 10px; background: white; }
        .item-card { border: 1px solid #eee; padding: 10px; border-radius: 8px; margin-bottom: 10px; background: #fafafa; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary shadow mb-4"><div class="container"><h3>🏙️ MEGA MALL 2026</h3><a href="/admin" class="btn btn-warning">Mall Dashboard</a></div></nav>
    <div class="container-fluid px-5">
        {% if msg %}<div class="alert alert-success">{{msg}}</div>{% endif %}
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
                    <h4 class="text-center">Your Shopping Bag</h4><hr>
                    <div style="max-height: 300px; overflow-y: auto;">
                        <table class="table table-sm small">
                            {% for i in cart %}<tr><td>{{i.name}}</td><td>x{{i.qty}}</td><td>Rs {{i.price}}</td></tr>{% endfor %}
                        </table>
                    </div>
                    <div class="bg-dark text-white p-3 rounded mt-2">
                        <div class="d-flex justify-content-between"><span>Subtotal:</span> <span>Rs {{total}}</span></div>
                        <div class="d-flex justify-content-between text-warning"><span>Discount:</span> <span>- Rs {{disc}}</span></div>
                        <hr><h3 class="text-center">Total: Rs {{total - disc}}</h3>
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
    <h2 style="color: green;">Total Revenue: Rs {{revenue}}</h2><hr>
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