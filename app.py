from app_instance import app
from layout import get_layout

app.layout = get_layout()
import callbacks


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
