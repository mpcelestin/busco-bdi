from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/images/products'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# Email configuration (add these after app config)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mugishapc1@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'oljteuieollgwxxf'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'mugishapc1@gmail.com'



# Initialize database
def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    
    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  price REAL,
                  image_path TEXT,
                  phone TEXT,
                  approved INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  message TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  read INTEGER DEFAULT 0)''')


    # Create admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    
    # Check if admin exists, if not create default
    c.execute("SELECT * FROM admin WHERE email = 'busco@gmail.com'")
    if not c.fetchone():
        hashed_password = generate_password_hash('0220Busco', method='pbkdf2:sha256')
        c.execute("INSERT INTO admin (email, password) VALUES (?, ?)", 
                 ('busco@gmail.com', hashed_password))
    
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def home():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE approved = 1 ORDER BY created_at DESC")
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE email = ?", (email,))
        admin = c.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin[2], password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('admin.html')



@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    phone = request.form.get('phone')
    
    # Handle file upload
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        image_path = f'images/products/{filename}'
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (name, description, price, image_path, phone, approved) VALUES (?, ?, ?, ?, ?, ?)",
             (name, description, price, image_path, phone, 1))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/approve_product/<int:product_id>')
def approve_product(product_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("UPDATE products SET approved = 1 WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/delete_product/<int:product_id>')
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    
    # Get image path to delete the file
    c.execute("SELECT image_path FROM products WHERE id = ?", (product_id,))
    result = c.fetchone()
    if result:
        image_path = result[0]
        try:
            os.remove(os.path.join('static', image_path))
        except:
            pass
    
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if not all([name, email, message]):
        return jsonify({'error': 'All fields are required'}), 400
    
    # Save to database
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
             (name, email, message))
    conn.commit()
    conn.close()
    
    # Send email (updated with better error handling)
    try:
        msg = MIMEText(f"""
        New message from BUSCO website contact form:
        
        Name: {name}
        Email: {email}
        Message: 
        {message}
        
        Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        msg['Subject'] = f"BUSCO Contact: New message from {name}"
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = 'busco@gmail.com'  # Your receiving email
        
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.ehlo()
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(
                app.config['MAIL_DEFAULT_SENDER'],
                ['busco@gmail.com'],  # Can add multiple recipients
                msg.as_string()
            )
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        # Log the error but don't fail the request since we saved to DB
    
    return jsonify({'success': True})

# Add admin message viewing route
@app.route('/admin/messages')
def view_messages():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM messages ORDER BY read ASC, created_at DESC")
        messages = c.fetchall()
        
        # Debug output
        print(f"Found {len(messages)} messages:")
        for msg in messages:
            print(dict(msg))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        messages = []
    finally:
        conn.close()
    
    return render_template('admin_messages.html', messages=messages)

# Add route to mark messages as read
@app.route('/admin/mark_read/<int:message_id>')
def mark_message_read(message_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("UPDATE messages SET read = 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Add this route to show messages count in admin dashboard
@app.route('/admin/messages_count')
def messages_count():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE read = 0")
    unread_count = c.fetchone()[0]
    conn.close()
    
    return jsonify({'unread_count': unread_count})

# Update the admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    
    # Get products
    c.execute("SELECT * FROM products ORDER BY approved ASC, created_at DESC")
    products = c.fetchall()
    
    # Get unread messages count
    c.execute("SELECT COUNT(*) FROM messages WHERE read = 0")
    unread_count = c.fetchone()[0]
    
    conn.close()
    
    return render_template('admin.html', products=products, dashboard=True, unread_count=unread_count)

@app.route('/admin/get_message/<int:message_id>')
def get_message(message_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
    message = c.fetchone()
    conn.close()
    
    if message:
        return jsonify({
            'id': message['id'],
            'name': message['name'],
            'email': message['email'],
            'message': message['message'],
            'created_at': message['created_at'],
            'read': message['read']
        })
    return jsonify({'error': 'Message not found'}), 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)