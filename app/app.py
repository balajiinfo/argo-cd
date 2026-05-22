from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

todos = ["Learn Argo CD", "Practice GitOps", "Deploy to Kubernetes"]

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>My Todo App - GitOps Demo</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; background: #f0f4f8; }
    .card { background: white; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
    h1 { color: #2d3748; margin-top: 0; }
    .badge { background: #667eea; color: white; font-size: 12px; padding: 3px 10px; border-radius: 20px; margin-left: 8px; }
    ul { list-style: none; padding: 0; }
    li { padding: 12px 16px; background: #f7fafc; margin: 8px 0; border-radius: 8px; border-left: 4px solid #667eea; }
    form { display: flex; gap: 8px; margin-top: 20px; }
    input { flex: 1; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; }
    button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; }
    button:hover { background: #5a67d8; }
    .version { text-align: center; margin-top: 20px; font-size: 12px; color: #a0aec0; }
  </style>
</head>
<body>
  <div class="card">
    <h1>My Todo App <span class="badge">v1.0</span></h1>
    <p style="color:#718096">Deployed via Argo CD + GitOps 🚀</p>
    <ul>
      {% for todo in todos %}
        <li>{{ todo }}</li>
      {% endfor %}
    </ul>
    <form method="POST" action="/add">
      <input type="text" name="todo" placeholder="Add a new task..." required />
      <button type="submit">Add</button>
    </form>
    <p class="version">Running on: {{ hostname }} | Pod ready ✅</p>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, todos=todos, hostname=os.environ.get("HOSTNAME", "local"))

@app.route("/add", methods=["POST"])
def add():
    todo = request.form.get("todo", "").strip()
    if todo:
        todos.append(todo)
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
