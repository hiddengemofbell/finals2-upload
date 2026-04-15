import os
import calendar
from datetime import datetime, timedelta
from flask import Flask, render_template, abort, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super-secret-admin-key-2026'
MAX_BOOKINGS_PER_DATE = 3

USERS = {
    'admin@example.com': {
        'password': 'admin123',
        'role': 'admin',
        'name': 'Admin User'
    },
    'staff@example.com': {
        'password': 'staff123',
        'role': 'staff',
        'name': 'Staff Member'
    },
    'customer@example.com': {
        'password': 'user123',
        'role': 'user',
        'name': 'Regular Customer'
    }
}

ROLE_REDIRECT = {
    'admin': 'admin_dashboard',
    'staff': 'staff_dashboard',
    'user': 'user_dashboard'
}


def get_current_user():
    user_data = session.get('user')
    if not user_data:
        return None
    return user_data

# Defining the albums
ALBUM = [
    {"name": "birthday-cake", "title": "Birthday Cake", "cover": "cake2.jpg"},
    {"name": "Anniversary-cake", "title": "Anniversary Cake", "cover": "cake2.jpg"},
    {"name": "Christening-cake", "title": "Christening Cake", "cover": "cake2.jpg"},
    {"name": "Gender-Reveal-cake", "title": "Gender Reveal Cake", "cover": "cake2.jpg"},
    {"name": "Graduation-cake", "title": "Graduation Cake", "cover": "cake2.jpg"},
    {"name": "Minimalist-cake", "title": "Minimalist Cake", "cover": "cake2.jpg"},
    {"name": "Printed-Edible-cake", "title": "Printed Edible Cake", "cover": "cake2.jpg"},
    {"name": "Reunion-cake", "title": "Reunion Cake", "cover": "cake2.jpg"},
    {"name": "Wedding-cake", "title": "Wedding Cake", "cover": "cake2.jpg"}
]

# HOME
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# GALLERY
@app.route('/gallery')
def gallery():
    return render_template('gallery.html', albums=ALBUM)


# ALBUM PAGE
@app.route('/gallery/<album_name>')
def album(album_name):
    album_names = [a["name"] for a in ALBUM]

    if album_name not in album_names:
        abort(404)

    # REAL connection to your folder
    image_folder = os.path.join('static', 'images', album_name)

    images = os.listdir(image_folder)  # gets all files in folder

    return render_template(
        'albums/album.html',
        album=album_name,
        images=images
    )

# BOOKINGS
booking_data = []

@app.route('/bookings')
def bookings():
    return render_template('bookings.html', bookings=booking_data)

@app.route('/book', methods=['GET', 'POST'])
def book():
    calendar.setfirstweekday(calendar.SUNDAY)
    now = datetime.now()
    today = now.date().isoformat()
    current_month = now.month
    current_year = now.year
    try:
        month = int(request.args.get('month', current_month))
        year = int(request.args.get('year', current_year))
    except ValueError:
        month = current_month
        year = current_year

    if year < current_year or (year == current_year and month < current_month):
        month = current_month
        year = current_year

    if month < 1 or month > 12:
        month = current_month
        year = current_year

    month_days = calendar.monthcalendar(year, month)

    counts_by_date = {}
    for booking in booking_data:
        date_str = booking.get('event_date', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            continue
        counts_by_date[date_obj] = counts_by_date.get(date_obj, 0) + 1

    bookings_by_day = {}
    for date_obj, count in counts_by_date.items():
        if date_obj.year == year and date_obj.month == month:
            bookings_by_day[date_obj.day] = count

    blocked_dates = [date_obj.strftime('%Y-%m-%d') for date_obj, count in counts_by_date.items() if count >= MAX_BOOKINGS_PER_DATE and date_obj.year == year and date_obj.month == month]
    error = None

    if request.method == 'POST':
        event_date = request.form.get('event_date', '')
        event_time = request.form.get('event_time', '')
        selected_date = None
        if event_date:
            try:
                selected_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            except ValueError:
                selected_date = None

        if not event_date:
            error = 'Please select a pickup date.'
        elif not event_time:
            error = 'Please choose a pickup time.'
        elif event_time < '08:00':
            error = 'Pickup can only start at 08:00 or later.'
        elif selected_date and counts_by_date.get(selected_date, 0) >= MAX_BOOKINGS_PER_DATE:
            error = f"The selected date {event_date} is already fully booked. Please choose another date."
        else:
            booking = {
                'name': request.form.get('name', ''),
                'email': request.form.get('email', ''),
                'phone': request.form.get('phone', ''),
                'address': request.form.get('address', ''),
                'social': request.form.get('social', ''),
                'event_date': event_date,
                'event_time': event_time,
                'cake_type': request.form.get('cake_type', 'Birthday'),
                'total': int(request.form.get('total', 1800)),
                'notes': request.form.get('notes', '')
            }
            booking_data.append(booking)
            return redirect(url_for('bookings'))

    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    show_calendar = len(blocked_dates) > 0
    has_prev = not (year == current_year and month == current_month)

    return render_template(
        'booking-form.html',
        month_name=calendar.month_name[month],
        year=year,
        month=month,
        month_days=month_days,
        bookings_by_day=bookings_by_day,
        blocked_dates=blocked_dates,
        max_bookings_per_date=MAX_BOOKINGS_PER_DATE,
        today=today,
        error=error,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        has_prev=has_prev,
        show_calendar=show_calendar
    )


# CONTACT
@app.route('/contact')
def contact():
    return render_template('contact.html')


# ABOUT US
@app.route('/about')
def about():
    return render_template('about.html')

# AUTHENTICATION
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    message = None
    active_tab = 'login'
    if request.method == 'POST':
        form_type = request.form.get('form_type', 'login')
        if form_type == 'signup':
            active_tab = 'signup'
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not name or not email or not password:
                error = 'Please complete all sign up fields.'
            elif password != confirm_password:
                error = 'Passwords do not match.'
            elif email in USERS:
                error = 'This email is already registered.'
            else:
                USERS[email] = {
                    'password': password,
                    'role': 'user',
                    'name': name
                }
                message = 'Sign up completed successfully. Please sign in below.'
                active_tab = 'login'
        else:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            user = USERS.get(email)
            if not user or user.get('password') != password:
                error = 'Invalid email or password. Please try again.'
            else:
                session['user'] = {
                    'email': email,
                    'name': user['name'],
                    'role': user['role']
                }
                next_route = ROLE_REDIRECT.get(user['role'], 'user_dashboard')
                return redirect(url_for(next_route))
    return render_template('login.html', error=error, message=message, active_tab=active_tab)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return redirect(url_for(ROLE_REDIRECT.get(user['role'], 'user_dashboard')))

@app.route('/admin/dashboard')
def admin_dashboard():
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('login'))

    today = datetime.now().date()
    valid_bookings = []
    for i, booking in enumerate(booking_data):
        try:
            event_date = datetime.strptime(booking.get('event_date', ''), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            continue
        booking_record = booking.copy()
        booking_record['id'] = i
        booking_record['event_date_obj'] = event_date
        booking_record['status'] = 'Upcoming' if event_date >= today else 'Completed'
        booking_record['cake_type'] = booking.get('cake_type', 'Birthday')  # Add cake type
        booking_record['total'] = booking.get('total', 1800)  # Add total price
        valid_bookings.append(booking_record)

    sorted_bookings = sorted(valid_bookings, key=lambda b: b['event_date_obj'], reverse=True)
    total_bookings = len(valid_bookings)
    upcoming_orders = sum(1 for booking in valid_bookings if booking['event_date_obj'] >= today)
    last_booking = sorted_bookings[0] if sorted_bookings else None
    oldest_date = min((booking['event_date_obj'] for booking in valid_bookings), default=today)
    days_tracked = max((today - oldest_date).days + 1, 1) if valid_bookings else 1
    average_per_day = round(total_bookings / days_tracked, 1) if valid_bookings else 0
    revenue = sum(booking['total'] for booking in valid_bookings)
    next_event = min((booking['event_date_obj'] for booking in valid_bookings if booking['event_date_obj'] >= today), default=None)

    stats = {
        'total_bookings': total_bookings,
        'revenue': f'₱{revenue:,}',
        'upcoming_orders': upcoming_orders,
        'last_booking_date': last_booking['event_date_obj'].strftime('%b %d, %Y') if last_booking else '—',
        'next_event_date': next_event.strftime('%b %d, %Y') if next_event else 'No upcoming order',
        'avg_per_day': average_per_day,
        'days_tracked': days_tracked
    }

    # Convert bookings to JSON-serializable format for JavaScript
    recent_orders = []
    for booking in sorted_bookings[:20]:
        recent_orders.append({
            'id': booking['id'],
            'name': booking['name'],
            'cake_type': booking['cake_type'],
            'event_date': booking['event_date'],
            'event_time': booking['event_time'],
            'total': booking['total'],
            'status': booking['status']
        })

    return render_template('admin_dashboard.html', title='Admin Dashboard', user=user, stats=stats, recent_orders=recent_orders)

@app.route('/admin/calendar')
def admin_calendar():
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Prepare booking data for calendar
    calendar_bookings = []
    for i, booking in enumerate(booking_data):
        try:
            event_date = datetime.strptime(booking.get('event_date', ''), '%Y-%m-%d').date()
            calendar_bookings.append({
                'id': i,
                'date': booking['event_date'],
                'name': booking['name'],
                'email': booking['email'],
                'phone': booking['phone'],
                'address': booking['address'],
                'cake_type': booking.get('cake_type', 'Birthday'),
                'total': booking.get('total', 1800),
                'event_time': booking['event_time'],
                'notes': booking.get('notes', ''),
                'time': booking['event_time']
            })
        except (ValueError, TypeError):
            continue
    
    return render_template('admin_calendar.html', title='Calendar', user=user, bookings=calendar_bookings)

@app.route('/admin/orders')
def admin_orders():
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_orders.html', title='Orders', user=user, bookings=booking_data)

@app.route('/admin/settings')
def admin_settings():
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_settings.html', title='Settings', user=user)

@app.route('/staff/dashboard')
def staff_dashboard():
    user = get_current_user()
    if not user or user.get('role') != 'staff':
        return redirect(url_for('login'))
    return render_template('dashboard.html', title='Staff Dashboard', user=user)

@app.route('/user/dashboard')
def user_dashboard():
    user = get_current_user()
    if not user or user.get('role') != 'user':
        return redirect(url_for('login'))
    return render_template('dashboard.html', title='User Dashboard', user=user)

# 404 ERROR HANDLER
def page_not_found(e):
    return render_template('404.html'), 404

app.register_error_handler(404, page_not_found)

if __name__ == '__main__':
    app.run(debug=True)