from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime, timedelta # timedelta zaroori hai time shift ke liye

app = Flask(__name__)
app.secret_key = "mega_mall_ultra_key"

# ... (Inventory wala hissa wahi rehne dein) ...

sales_history = []

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if cart:
        # 1. TIME FIX: UTC se Indian Time (+5:30) mein badalna
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        formatted_time = ist_time.strftime("%I:%M %p") # 12-hour format with AM/PM
        
        # 2. SUMMARY FIX: Items ko text mein badalna
        # Purani galti: cart.items (Jo dict method dikha raha tha)
        # Sahi tarika: List comprehension se naam nikalna
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
        return redirect('/')
    return redirect('/')

# ... (Baki Admin aur HTML_TEMPLATE wahi rehne dein) ...
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