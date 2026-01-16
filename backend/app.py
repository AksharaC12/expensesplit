from flask import Flask
from flask_cors import CORS

from auth import auth_bp
from groups import groups_bp

app = Flask(__name__)

# ✅ Enable CORS (REQUIRED for Flutter Web)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# ✅ Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)

# ================= RUN =================
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
