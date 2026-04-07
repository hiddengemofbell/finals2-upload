import os
import calendar
from datetime import datetime, timedelta
from flask import Flask, render_template, abort, request, redirect, url_for

app = Flask(__name__)
MAX_BOOKINGS_PER_DATE = 3

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


if __name__ == '__main__':
    app.run(debug=True)