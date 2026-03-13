import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta

app = Flask(__name__)

import os

# Secret key
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# MySQL configuration (Railway + Local compatible)
app.config['MYSQL_HOST'] = os.environ.get("MYSQLHOST", "mysql.railway.internal")
app.config['MYSQL_USER'] = os.environ.get("MYSQLUSER", "root")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQLPASSWORD", "kDcRVliHneMcCVQOSruWChRnYQfJIYvU")
app.config['MYSQL_DB'] = os.environ.get("MYSQLDATABASE", "railway")
app.config['MYSQL_PORT'] = int(os.environ.get("MYSQLPORT", 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'posters')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

mysql = MySQL(app)

@app.template_filter('format_duration')
def format_duration(minutes):
    if not minutes: return "0m"
    h = minutes // 60
    m = minutes % 60
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"

# Helper function to check if user is logged in
def is_logged_in():
    return 'user_id' in session

# Helper function to check if admin is logged in
def is_admin_logged_in():
    return 'admin_id' in session

# ROUTES

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    cursor.close()
    return render_template('user/index.html', movies=movies)

# User Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('user/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            
    return render_template('user/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin123': # Simple hardcoded check as fallback/initial
             session['admin_id'] = 1 # Mock ID or fetch from DB
             session['admin_name'] = 'Admin'
             return redirect(url_for('admin_dashboard'))
        
        # Or DB check (Recommended)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
        cursor.close()
        
        if admin and (check_password_hash(admin['password'], password) or password == 'admin123'): # Allow hardcoded for easy testing
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
            
    return render_template('admin/admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    
    # Fetch stats
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM movies")
    movie_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM bookings")
    booking_count = cursor.fetchone()['count']
    cursor.execute("SELECT SUM(total_amount) as revenue FROM bookings")
    revenue = cursor.fetchone()['revenue'] or 0
    cursor.close()
    
    return render_template('admin/dashboard.html', movie_count=movie_count, booking_count=booking_count, revenue=revenue)

@app.route('/admin/movies')
def manage_movies():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    cursor = mysql.connection.cursor()
    
    # Fetch movies
    cursor.execute("SELECT * FROM movies ORDER BY created_at DESC")
    movies = cursor.fetchall()
    
    # Fetch shows for each movie to display in the table
    for movie in movies:
        cursor.execute("SELECT *, screen FROM shows WHERE movie_id = %s ORDER BY show_time ASC", (movie['id'],))
        movie['shows'] = cursor.fetchall()
        
    cursor.close()
    return render_template('admin/manage_movies.html', movies=movies)

@app.route('/admin/add_movie', methods=['GET', 'POST'])
def add_movie():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        duration_h = int(request.form.get('duration_h', 0))
        duration_m = int(request.form.get('duration_m', 0))
        duration = (duration_h * 60) + duration_m
        genre = request.form['genre']
        
        # Handle image upload
        poster_image = ''
        if 'poster_image' in request.files:
            file = request.files['poster_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                poster_image = filename
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO movies (title, description, poster_image, duration_minutes, genre)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, poster_image, duration, genre))
        mysql.connection.commit()
        movie_id = cursor.lastrowid

        # Insert any manually provided show datetimes (one per line: YYYY-MM-DD HH:MM)
        show_times_raw = request.form.get('show_times', '').strip()
        if show_times_raw:
            price_silver = request.form.get('price_silver', '150')
            price_gold = request.form.get('price_gold', '200')
            price_platinum = request.form.get('price_platinum', '250')
            lines = [l.strip() for l in show_times_raw.splitlines() if l.strip()]
            for line in lines:
                try:
                    dt = datetime.strptime(line, '%Y-%m-%d %H:%M')
                except Exception:
                    try:
                        # try ISO parse
                        dt = datetime.fromisoformat(line)
                    except Exception:
                        continue
                show_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("""
                    INSERT INTO shows (movie_id, show_time, price_silver, price_gold, price_platinum)
                    VALUES (%s, %s, %s, %s, %s)
                """, (movie_id, show_dt, price_silver, price_gold, price_platinum))
            mysql.connection.commit()

        # Auto-generate shows if requested
        if request.form.get('generate_shows'):
            try:
                generate_days = int(request.form.get('generate_days', 3))
            except ValueError:
                generate_days = 3
            times_raw = request.form.get('generate_times', '12:00,15:30,19:00')
            times = [t.strip() for t in times_raw.split(',') if t.strip()]
            # Prices for generated shows (optional inputs)
            price_silver = request.form.get('price_silver', '150')
            price_gold = request.form.get('price_gold', '200')
            price_platinum = request.form.get('price_platinum', '250')

            # Insert shows for the next N days at the specified times
            for day_offset in range(generate_days):
                show_date = (datetime.now().date() + timedelta(days=day_offset))
                for t in times:
                    try:
                        tm = datetime.strptime(t, '%H:%M').time()
                    except Exception:
                        # skip invalid time formats
                        continue
                    show_dt = datetime.combine(show_date, tm).strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute("""
                        INSERT INTO shows (movie_id, show_time, price_silver, price_gold, price_platinum)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (movie_id, show_dt, price_silver, price_gold, price_platinum))
            mysql.connection.commit()

        cursor.close()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('manage_movies'))
        
    return render_template('admin/add_movie.html')

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()

    # Convert YouTube URL to embeddable format if trailer_url exists
    if movie and movie['trailer_url']:
        trailer_url = movie['trailer_url']
        print(f"Original trailer URL: {trailer_url}")  # Debug log
        if 'youtube.com/watch?v=' in trailer_url:
            video_id = trailer_url.split('v=')[1]
            ampersand_position = video_id.find('&')
            if ampersand_position != -1:
                video_id = video_id[:ampersand_position]
            movie['trailer_url'] = f"https://www.youtube.com/embed/{video_id}"
            print(f"Processed trailer URL: {movie['trailer_url']}")  # Debug log
        elif 'youtu.be/' in trailer_url:  # Handle shortened YouTube URLs
            video_id = trailer_url.split('youtu.be/')[1]
            ampersand_position = video_id.find('?')
            if ampersand_position != -1:
                video_id = video_id[:ampersand_position]
            movie['trailer_url'] = f"https://www.youtube.com/embed/{video_id}"
            print(f"Processed trailer URL: {movie['trailer_url']}")  # Debug log

    # Fetch shows for this movie
    cursor.execute("SELECT *, screen FROM shows WHERE movie_id = %s ORDER BY show_time", (movie_id,))
    shows = cursor.fetchall()
    cursor.close()

    return render_template('user/movie_details.html', movie=movie, shows=shows)


@app.route('/price_list')
def price_list():
    """Show price list aggregated from `shows` table."""
    cursor = mysql.connection.cursor()
    # Get distinct price combinations
    cursor.execute("SELECT screen, price_silver, price_gold, price_platinum FROM shows GROUP BY screen, price_silver, price_gold, price_platinum ORDER BY price_silver ASC")
    prices = cursor.fetchall()

    # Also compute minimums (useful to show lowest available price per tier)
    cursor.execute("SELECT MIN(price_silver) as min_silver, MIN(price_gold) as min_gold, MIN(price_platinum) as min_platinum FROM shows")
    mins = cursor.fetchone()
    cursor.close()

    return render_template('user/price_list.html', prices=prices, mins=mins)

@app.route('/admin/add_show/<int:movie_id>', methods=['GET', 'POST'])
def add_show(movie_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        screen = request.form['screen']   # ✅ NEW FIELD
        show_time = request.form['show_time']
        price_silver = request.form['price_silver']
        price_gold = request.form['price_gold']
        price_platinum = request.form['price_platinum']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO shows 
            (movie_id, screen, show_time, price_silver, price_gold, price_platinum)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (movie_id, screen, show_time, price_silver, price_gold, price_platinum))
        
        mysql.connection.commit()
        cursor.close()

        flash('Show added successfully!', 'success')
        return redirect(url_for('manage_movies'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    
    return render_template('admin/add_show.html', movie=movie)

@app.route('/book/<int:show_id>', methods=['GET', 'POST'])
def book_seats(show_id):
    if not is_logged_in():
        flash('Please login to book tickets.', 'info')
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    
    # Fetch show and movie details
    cursor.execute("""
        SELECT s.*, m.title, m.poster_image 
        FROM shows s 
        JOIN movies m ON s.movie_id = m.id 
        WHERE s.id = %s
    """, (show_id,))
    show = cursor.fetchone()
    
    if not show:
        cursor.close()
        flash('Show not found or has been canceled.', 'danger')
        return redirect(url_for('home'))
    
    # Fetch already booked seats (Confirmed)
    cursor.execute("SELECT seats FROM bookings WHERE show_id = %s AND status = 'Confirmed'", (show_id,))
    confirmed_bookings = cursor.fetchall()
    booked_seats = []
    for booking in confirmed_bookings:
        booked_seats.extend(booking['seats'].split(','))

    # Fetch pending seats (within last 10 minutes)
    cursor.execute("""
        SELECT seats FROM bookings 
        WHERE show_id = %s 
        AND status = 'Pending' 
        AND booking_date >= NOW() - INTERVAL 10 MINUTE
    """, (show_id,))
    pending_bookings = cursor.fetchall()
    pending_seats = []
    for booking in pending_bookings:
        pending_seats.extend(booking['seats'].split(','))
        
    if request.method == 'POST':
        selected_seats = request.form['selected_seats'] # Comma separated
        total_amount = request.form['total_amount']
        user_id = session.get('user_id')

        # Defensive checks: ensure user and show exist to avoid FK errors
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            flash('User account not found. Please login again.', 'danger')
            return redirect(url_for('login'))

        cursor.execute("SELECT id FROM shows WHERE id = %s", (show_id,))
        if not cursor.fetchone():
            cursor.close()
            flash('Selected show not found. Please choose another show.', 'danger')
            return redirect(url_for('home'))

        # Insert booking with Pending status and handle DB integrity errors
        try:
            cursor.execute("""
                INSERT INTO bookings (user_id, show_id, seats, total_amount, status)
                VALUES (%s, %s, %s, %s, 'Pending')
            """, (user_id, show_id, selected_seats, total_amount))
            mysql.connection.commit()
            booking_id = cursor.lastrowid
            cursor.close()
            flash('Seats reserved! Please complete payment.', 'info')
            return redirect(url_for('payment', booking_id=booking_id))
        except pymysql.err.IntegrityError:
            mysql.connection.rollback()
            cursor.close()
            flash('Failed to create booking due to invalid reference.', 'danger')
            return redirect(url_for('home'))
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            flash(f'Error creating booking: {str(e)}', 'danger')
            return redirect(url_for('home'))
    
    cursor.close()
    return render_template('user/seat_booking.html', show=show, booked_seats=booked_seats, pending_seats=pending_seats)

@app.route('/payment/<int:booking_id>')
def payment(booking_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT b.*, m.title 
        FROM bookings b 
        JOIN shows s ON b.show_id = s.id 
        JOIN movies m ON s.movie_id = m.id 
        WHERE b.id = %s AND b.user_id = %s AND b.status = 'Pending'
    """, (booking_id, session['user_id']))
    booking = cursor.fetchone()
    cursor.close()
    
    if not booking:
        flash('Invalid booking or payment already completed.', 'warning')
        return redirect(url_for('home'))
        
    return render_template('user/payment.html', booking=booking)


# Debug route to list all registered endpoints (helpful for BuildError troubleshooting)
@app.route('/__routes__')
def _list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint} -> {rule}")
    return '<br>'.join(sorted(routes))

@app.route('/process_payment/<int:booking_id>', methods=['POST'])
def process_payment(booking_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    # Simulate payment processing...
    # In a real app, this is where Stripe/Razorpay would verify the transaction
    
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE bookings SET status = 'Confirmed' WHERE id = %s AND user_id = %s", (booking_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()
    
    flash('Payment Successful! Booking Confirmed.', 'success')
    return redirect(url_for('booking_confirmation', booking_id=booking_id))

@app.route('/confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT b.*, s.show_time, s.screen, m.title, u.name as user_name 
        FROM bookings b 
        JOIN shows s ON b.show_id = s.id 
        JOIN movies m ON s.movie_id = m.id 
        JOIN users u ON b.user_id = u.id 
        WHERE b.id = %s AND b.user_id = %s AND b.status = 'Confirmed'
    """, (booking_id, session['user_id']))
    booking = cursor.fetchone()
    cursor.close()
    
    if not booking:
        flash('Booking not confirmed or access denied.', 'danger')
        return redirect(url_for('home'))
        
    return render_template('user/confirmation.html', booking=booking)

@app.route('/my_bookings')
def my_bookings():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT b.*, m.title, m.poster_image, s.show_time 
        FROM bookings b 
        JOIN shows s ON b.show_id = s.id 
        JOIN movies m ON s.movie_id = m.id 
        WHERE b.user_id = %s 
        ORDER BY b.booking_date DESC
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    cursor.close()
    
    return render_template('user/booking_history.html', bookings=bookings)

# Admin Management Routes
@app.route('/admin/bookings')
def admin_bookings():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT b.*, u.name as user_name, m.title, s.show_time 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        JOIN shows s ON b.show_id = s.id 
        JOIN movies m ON s.movie_id = m.id 
        ORDER BY b.booking_date DESC
    """)
    bookings = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/delete_movie/<int:movie_id>')
def delete_movie(movie_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    mysql.connection.commit()
    cursor.close()
    flash('Movie deleted successfully.', 'info')
    return redirect(url_for('manage_movies'))

@app.route('/admin/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        duration_h = int(request.form.get('duration_h', 0))
        duration_m = int(request.form.get('duration_m', 0))
        duration = (duration_h * 60) + duration_m
        genre = request.form['genre']
        trailer_url = request.form['trailer_url']  # Get the trailer URL from the form

        # Get existing movie to keep old image if no new one is uploaded
        cursor.execute("SELECT poster_image FROM movies WHERE id = %s", (movie_id,))
        existing_movie = cursor.fetchone()
        poster_image = existing_movie['poster_image']

        # Handle image upload
        if 'poster_image' in request.files:
            file = request.files['poster_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                poster_image = filename

        cursor.execute("""
            UPDATE movies 
            SET title=%s, description=%s, poster_image=%s, duration_minutes=%s, genre=%s, trailer_url=%s 
            WHERE id=%s
        """, (title, description, poster_image, duration, genre, trailer_url, movie_id))
        mysql.connection.commit()
        cursor.close()
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('manage_movies'))

    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()

    return render_template('admin/add_movie.html', movie=movie, is_edit=True)

@app.route('/admin/delete_show/<int:show_id>')
def delete_show(show_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM shows WHERE id = %s", (show_id,))
    mysql.connection.commit()
    cursor.close()
    flash('Show time removed successfully.', 'info')
    return redirect(url_for('manage_movies'))


@app.route('/cancel_booking/<int:booking_id>', methods=['POST', 'GET'])
def cancel_booking(booking_id):
    # Allow both users and admins to cancel bookings
    # Users can only cancel their own bookings; admins can cancel any
    if is_logged_in():
        # user-initiated cancellation
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM bookings WHERE id = %s AND user_id = %s", (booking_id, session['user_id']))
        booking = cursor.fetchone()
        if not booking:
            cursor.close()
            flash('Booking not found or access denied.', 'warning')
            return redirect(url_for('my_bookings'))

        # Only allow canceling Pending or Confirmed bookings
        if booking['status'] not in ('Pending', 'Confirmed'):
            cursor.close()
            flash('Booking cannot be cancelled.', 'info')
            return redirect(url_for('my_bookings'))

        cursor.execute("UPDATE bookings SET status = 'Canceled' WHERE id = %s", (booking_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Booking cancelled successfully.', 'success')
        return redirect(url_for('my_bookings'))

    if is_admin_logged_in():
        # admin-initiated cancellation
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            cursor.close()
            flash('Booking not found.', 'warning')
            return redirect(url_for('admin_bookings'))

        cursor.execute("UPDATE bookings SET status = 'Canceled' WHERE id = %s", (booking_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Booking cancelled by admin.', 'info')
        return redirect(url_for('admin_bookings'))

    # Not logged in
    flash('Please login to cancel bookings.', 'info')
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT m.title AS movie_name, s.price_silver, s.price_gold, s.price_platinum FROM shows s JOIN movies m ON s.movie_id = m.id")
    prices = cursor.fetchall()
    cursor.close()
    return render_template('pricing.html', prices=prices)

if __name__ == '__main__':
    # Disable the Werkzeug reloader when running under the VSCode debugger
    # to avoid a SystemExit: 3 from the reloader process.
    # Print registered routes to help debug Not Found errors
    print('Registered routes:')
    for rule in app.url_map.iter_rules():
        print(f" - {rule.endpoint}: {rule}")
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ===============================
# SECURITY
# ===============================
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# ===============================
# MYSQL CONFIG (RAILWAY READY)
# ===============================
app.config['MYSQL_HOST'] = os.environ.get("MYSQLHOST", "127.0.0.1")
app.config['MYSQL_USER'] = os.environ.get("MYSQLUSER", "root")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQLPASSWORD", "")
app.config['MYSQL_DB'] = os.environ.get("MYSQLDATABASE", "movie_booking")
app.config['MYSQL_PORT'] = int(os.environ.get("MYSQLPORT", 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# ===============================
# FILE UPLOAD CONFIG
# ===============================
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'posters')
app.config['ALLOWED_EXTENSIONS'] = {'png','jpg','jpeg','gif'}

mysql = MySQL(app)

# ===============================
# HELPER FUNCTIONS
# ===============================

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_logged_in():
    return 'user_id' in session

def is_admin_logged_in():
    return 'admin_id' in session


@app.template_filter('format_duration')
def format_duration(minutes):

    if not minutes:
        return "0m"

    h = minutes // 60
    m = minutes % 60

    if h > 0:
        return f"{h}h {m}m"

    return f"{m}m"


# ===============================
# HOME PAGE
# ===============================
@app.route('/')
def home():

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM movies")

    movies = cursor.fetchall()

    cursor.close()

    return render_template('user/index.html', movies=movies)


# ===============================
# USER LOGIN
# ===============================
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()

        cursor.close()

        if user and check_password_hash(user['password'], password):

            session['user_id'] = user['id']
            session['user_name'] = user['name']

            flash("Login successful","success")

            return redirect(url_for('home'))

        else:
            flash("Invalid email or password","danger")

    return render_template("user/login.html")


# ===============================
# REGISTER
# ===============================
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cursor = mysql.connection.cursor()

        cursor.execute(
        "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
        (name,email,password))

        mysql.connection.commit()

        cursor.close()

        flash("Registration successful","success")

        return redirect(url_for('login'))

    return render_template("user/register.html")


# ===============================
# LOGOUT
# ===============================
@app.route('/logout')
def logout():

    session.clear()

    flash("Logged out successfully","info")

    return redirect(url_for('login'))


# ===============================
# ADMIN LOGIN
# ===============================
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM admins WHERE username=%s",(username,))
        admin = cursor.fetchone()

        cursor.close()

        if admin and check_password_hash(admin['password'], password):

            session['admin_id'] = admin['id']
            session['admin_name'] = admin['username']

            return redirect(url_for('admin_dashboard'))

        flash("Invalid admin credentials","danger")

    return render_template("admin/admin_login.html")


# ===============================
# ADMIN DASHBOARD
# ===============================
@app.route('/admin/dashboard')
def admin_dashboard():

    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM movies")
    movie_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM bookings")
    booking_count = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(total_amount) as revenue FROM bookings")
    revenue = cursor.fetchone()['revenue'] or 0

    cursor.close()

    return render_template(
    "admin/dashboard.html",
    movie_count=movie_count,
    booking_count=booking_count,
    revenue=revenue)


# ===============================
# ROUTE DEBUG
# ===============================
@app.route('/__routes__')
def routes():

    route_list = []

    for rule in app.url_map.iter_rules():
        route_list.append(f"{rule.endpoint} -> {rule}")

    return "<br>".join(route_list)


# ===============================
# ABOUT PAGE
# ===============================
@app.route('/about')
def about():

    return render_template("about.html")


# ===============================
# PRICING PAGE
# ===============================
@app.route('/pricing')
def pricing():

    cursor = mysql.connection.cursor()

    cursor.execute("""
    SELECT m.title,
           s.price_silver,
           s.price_gold,
           s.price_platinum
    FROM shows s
    JOIN movies m ON s.movie_id = m.id
    """)

    prices = cursor.fetchall()

    cursor.close()

    return render_template("pricing.html", prices=prices)


# ===============================
# RUN SERVER (RAILWAY SUPPORT)
# ===============================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    print("Starting Flask server on port:", port)

    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, "->", rule)

    app.run(host="0.0.0.0", port=port)



