import logging

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from flask import flash
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header

from sqldb import SqlDb
# OR
# from ormdb import OrmDb

log = logging.getLogger(__name__)
logging.basicConfig(
    filename="./runtime/log/app.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=" %(asctime)s %(message)s",
)

sql_db = SqlDb("./runtime/db/sql.db")
# OR
# orm_db = OrmDb("../runtime/db/orm.db")

app = Flask(__name__)
app.secret_key = b"G6z115u8WnfQ0UIJ"  # To get a unique basic 16 key: https://acte.ltd/utils/randomkeygen

csrf = CSRFProtect(app)

# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)

@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("/index.html")
@app.route("/signup.html", methods=["POST", "GET"])
def signup():

    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip()
        password = request.form["password"]
        confirm  = request.form["confirm_password"]

        # Validation
        if not username or not email or not password:
            error = "All fields are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        else:
            user = sql_db.create_user(username, email, password)
            if user is None:
                error = "That username or email is already taken. Please try another."
            else:
                log.info(f"New user registered: {username}")
                flash("Account created! Please log in.")
                return redirect(url_for("login"))

    return render_template("/signup.html", error=error)

@app.route("/login.html", methods=["POST", "GET"])
def login():

    error = None

    if request.method == "POST":
        email    = request.form["email"].strip()
        password = request.form["password"]

        user = sql_db.verify_login(email, password)
        if user is None:
            error = "Incorrect email or password."
            log.warning(f"Failed login attempt for email: {email}")
        else:
            # Save user info in the session
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["email"]    = user["email"]
            log.info(f"User logged in: {user['username']}")
            return redirect(url_for("index"))

    return render_template("/login.html", error=error)

@app.route("/logout")
def logout():
    username = session.get("username", "unknown")
    session.clear()
    log.info(f"User logged out: {username}")
    return redirect(url_for("login"))

@app.route("/request.html", methods=["POST", "GET"])
def send_request():
    if "user_id" not in session:
        flash("Please log in to access that page.")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        pass
    
    return render_template("/request.html")

@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")

@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        print(f"<From(email={email}, text='{text}')>")
        return render_template("/form.html")
    else:
        return render_template("/form.html")

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data)
    return "done"

if __name__ == "__main__":
    # app.logger.debug("Started")
    app.run(debug=True, host="0.0.0.0", port=5000)
