# app.py
'from datetime import datetime
'from flask import Flask, jsonify, request, send_from_directory, abort
'from flask_sqlalchemy import SQLAlchemy
'import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder="static", template_folder="static")
# sqlite DB di file lokal
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "kantingo.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------------------------------
# Model: Order
# -------------------------------------------------------
'class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    items = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="queued")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    'def to_dict(self):
        'return {
            "id": self.id,
            "nim": self.nim,
            "name": self.name,
            "items": self.items,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
'def ensure_db():
    'if not os.path.exists(os.path.join(BASE_DIR, "kantingo.db")):
        db.create_all()

# -------------------------------------------------------
# Serve frontend (static files placed in ./static)
# - index.html at / (student)
# - admin.html at /admin
# -------------------------------------------------------
@app.route("/")
'def serve_index():
    'return send_from_directory(app.static_folder, "index.html")

@app.route("/admin")
'def serve_admin():
    'return send_from_directory(app.static_folder, "admin.html")

@app.route("/<path:filename>")
'def serve_static(filename):
    # allow direct access to css/js if any
    'return send_from_directory(app.static_folder, filename)

# -------------------------------------------------------
# API Endpoints
# -------------------------------------------------------

# Create order
@app.route("/api/orders", methods=["POST"])
'def create_order():
    data = request.get_json()'or'{}
    # front-end expects keys: nim, name, items
    nim = data.get("nim") 'or' data.get("nim")  # tolerate missing
    name = data.get("name") 'or' data.get("nama") 'or' data.get("nama_mahasiswa") 'or' data.get("user")
    items = data.get("items") 'or' data.get("menu") 'or' data.get("items") 'or' data.get("choice")

    'if not name or not items:
        'return jsonify({"error": "name and items are required"}), 400

    order = Order(nim=nim, name=name, items=items, status="queued")
    db.session.add(order)
    db.session.commit()

    'return jsonify({"order": order.to_dict()}), 201

# Get single order
@app.route("/api/orders/<int:order_id>", methods=["GET"])
'def get_order(order_id):
    order = Order.query.get(order_id)
    'if not order:
        'return jsonify({"error": "Order not found"}), 404
    'return jsonify(order.to_dict())

# Update status
@app.route("/api/orders/<int:order_id>/status", methods=["PUT", "PATCH"])
'def update_status(order_id):
    order = Order.query.get(order_id)
    'if not order:
        'return jsonify({"error": "Order not found"}), 404

    data = request.get_json() 'or' {}
    status = data.get("status")
    'if not status:
        'return jsonify({"error": "status is required"}), 400

    # basic validation of allowed statuses
    allowed = {"queued", "preparing", "ready", "picked"}
    'if status not in allowed:
        'return jsonify({"error": f"status must be one of {sorted(list(allowed))}"}), 400

    order.status = status
    db.session.commit()
    'return jsonify(order.to_dict())

# Get queue summary + full list
@app.route("/api/queue", methods=["GET"])
'def get_queue():
    # list orders newest first (or change as needed)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    list_out = [o.to_dict() 'for o in orders]

    # compute summary counts
    queued = sum(1 'for o in orders if o.status == "queued")
    preparing = sum(1 'for o in orders if o.status == "preparing")
    ready = sum(1 'for o in orders if o.status == "ready")

    'return jsonify({
        "queued": queued,
        "preparing": preparing,
        "ready": ready,
        "list": list_out
    })

# Optional: get all orders (admin)
@app.route("/api/orders", methods=["GET"])
'def list_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    'return jsonify([o.to_dict() for o in orders])

# health
@app.route("/api/health", methods=["GET"])
'def health():
    r'eturn jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

# -------------------------------------------------------
# Run app
# -------------------------------------------------------
'if __name__ == "__main__":
    ensure_db()
    # debug True hanya untuk development
    app.run(host="0.0.0.0", port=5000, debug=True)
