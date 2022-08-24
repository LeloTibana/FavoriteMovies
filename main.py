from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///favoritemovies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
Bootstrap(app)


# Movies table
class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ranking = db.Column(db.String, unique=True,nullable=False)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, unique=True, nullable=False)
    rating = db.Column(db.String, unique=True, nullable=False)
    review = db.Column(db.String, unique=True, nullable=False)
    image_url = db.Column(db.String, unique=True, nullable=False)


db.create_all()


class EditForm(FlaskForm):
    rating = StringField('Rating out of 10')
    review = StringField('Your Review')
    submit = SubmitField('Submit')


#new_movie = Movies(
#    title="Phone Booth",
#    year=2002,
#    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#    rating=7.3,
#    ranking=10,
#    review="My favourite character was the caller.",
#    image_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#)

#db.session.add(new_movie)
#db.session.commit()


@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()

    # Looping through all the movies
    for x in range(len(all_movies)):
        # giving the movies a new ranking and then reversing the order in all_movies
        all_movies[x].ranking = len(all_movies) - x
    db.sesssion.commit()
    return render_template("index.html", movies=all_movies)

# Editing the rating of the movie
@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = EditForm()
    movie_id = request.args.get('id')
    movie = Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')

    movie_delete = Movies.query.get(movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for('home'))


# Movie API
TMDB_API = "8128f51b9b1ae02a3f68ad42092a4e0c"
TMDB_SEARCH = "https://api.themoviedb.org/3/search/movie?api_key=8128f51b9b1ae02a3f68ad42092a4e0c&language=en-US&page=1&include_adult=false"
tmdb_read_access = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4MTI4ZjUxYjliMWFlMDJhM2Y2OGFkNDIwOTJhNGUwYyIsInN1YiI6IjYzMDBlNmM3MDk3YzQ5MDA3YWEyMjBmNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.zvc3Q0gKg7aH-O2ce15llA2CUZwYyhIzxAOAWbezlZc"


# Form to add a movie
class addForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/add", methods=["POST", "GET"])
def add_movie():
    form = addForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(TMDB_SEARCH, params={"api_key": TMDB_API, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)


MOVIES_DETAILS_URL = "https://api.themoviedb.org/3/movie/{movie_id}?api_key=8128f51b9b1ae02a3f68ad42092a4e0c&language=en-US"
MOVIES_IMAGE_URL = "https://api.themoviedb.org/3/movie/{movie_id}/images?api_key=8128f51b9b1ae02a3f68ad42092a4e0c&language=en-US"


@app.route("/find")
def movie_data():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_api_url = f"{MOVIES_DETAILS_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params = {
            "api_key": MOVIES_DETAILS_URL,
            "language": "en-US"
        })
        data = response.json()
        new_movie = Movies(
            title=data["title"],

            # getting rid of the dash here
            year=data["release_date"].split("-")[0],
            image_url=f"{MOVIES_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect('home')


if __name__ == '__main__':
    app.run(debug=True)
