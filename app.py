from flask import Flask, render_template, abort

app = Flask(__name__)

# Define valid albums
GALLERY = ['wedding-cake', 'birthday-cake']

@app.route('/gallery/<album_name>')
def album(album_name):
    if album_name not in GALLERY:
        abort(404)  # if album doesn't exist
    return render_template(f'albums/{album_name}.html')

#HOME
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


#MENU
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

#BOOKINGS
@app.route('/bookings')
def bookings():
    return render_template('bookings.html')

#CONTACT
@app.route('/contact')
def contact():
    return render_template('contact.html')

#CALENDAR
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

#ABOUT US
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)