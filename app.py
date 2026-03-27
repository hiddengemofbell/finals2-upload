import os
from flask import Flask, render_template, abort

app = Flask(__name__)

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


# ALBUM PAGE (FIXED)
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
@app.route('/bookings')
def bookings():
    return render_template('bookings.html')


# CONTACT
@app.route('/contact')
def contact():
    return render_template('contact.html')


# CALENDAR
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


# ABOUT US
@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)