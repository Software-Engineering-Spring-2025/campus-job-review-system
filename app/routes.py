from flask import render_template, request, redirect, flash, url_for, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app.services.job_fetcher import fetch_job_listings
from app import app, db, bcrypt
from app.models import Reviews, User
from app.forms import RegistrationForm, LoginForm, ReviewForm

app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"


@app.route("/")
@app.route("/home")
def home():
    """An API for the user to be able to access the homepage through the navbar"""
    entries = Reviews.query.all()
    return render_template("index.html", entries=entries)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(
            "Account created successfully! Please log in with your credentials.",
            "success",
        )
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(
                "Login Unsuccessful. Please enter correct email and password.", "danger"
            )
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))


@app.route("/review/all")
def view_reviews():
    """An API for the user to view all the reviews entered with pagination"""
    page = request.args.get("page", 1, type=int)
    per_page = 5
    entries = Reviews.query.paginate(page=page, per_page=per_page)
    return render_template("view_reviews.html", entries=entries)


@app.route("/review/new", methods=["GET", "POST"])
@login_required
def new_review():
    form = ReviewForm()
    if form.validate_on_submit():
        review = Reviews(
            job_title=form.job_title.data,
            job_description=form.job_description.data,
            department=form.department.data,
            locations=form.locations.data,
            hourly_pay=form.hourly_pay.data,
            benefits=form.benefits.data,
            review=form.review.data,
            rating=form.rating.data,
            recommendation=form.recommendation.data,
            author=current_user,
        )
        db.session.add(review)
        db.session.commit()
        flash("Review submitted successfully!", "success")
        return redirect(url_for("view_reviews"))
    return render_template(
        "create_review.html", title="New Review", form=form, legend="Add your Review"
    )


@app.route("/review/<int:review_id>")
def review(review_id):
    review = Reviews.query.get_or_404(review_id)
    return render_template("review.html", review=review)


@app.route("/review/<int:review_id>/update", methods=["GET", "POST"])
@login_required
def update_review(review_id):
    review = Reviews.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    form = ReviewForm()
    if form.validate_on_submit():
        review.job_title = form.job_title.data
        review.job_description = form.job_description.data
        review.department = form.department.data
        review.locations = form.locations.data
        review.hourly_pay = form.hourly_pay.data
        review.benefits = form.benefits.data
        review.review = form.review.data
        review.rating = form.rating.data
        review.recommendation = form.recommendation.data
        db.session.commit()
        flash("Your review has been updated!", "success")
        return redirect(url_for("view_reviews"))
    elif request.method == "GET":
        form.job_title.data = review.job_title
        form.job_description.data = review.job_description
        form.department.data = review.department
        form.locations.data = review.locations
        form.hourly_pay.data = review.hourly_pay
        form.benefits.data = review.benefits
        form.review.data = review.review
        form.rating.data = review.rating
        form.recommendation.data = review.recommendation
    return render_template(
        "create_review.html", title="Update Review", form=form, legend="Update Review"
    )


@app.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Reviews.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash("Your review has been deleted!", "success")
    return redirect(url_for("view_reviews"))


@app.route("/dashboard")
def getVacantJobs():
    """
    An API for the users to see all the available vacancies and their details
    """
    return render_template("dashboard.html")


@app.route("/pageContentPost", methods=["POST", "GET"])
def page_content_post():
    """An API for the user to view specific reviews depending on the job title, location, and rating range with pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = 5  # Set items per page as desired

    # Retrieve form data
    search_title = request.form.get("search_title", "")
    search_location = request.form.get("search_location", "")
    min_rating = request.form.get("min_rating", type=int, default=1)
    max_rating = request.form.get("max_rating", type=int, default=5)

    # Initial query for reviews
    query = Reviews.query

    # Apply filters if search fields are filled
    if search_title.strip():
        query = query.filter(Reviews.job_title.ilike(f"%{search_title}%"))
    if search_location.strip():
        query = query.filter(Reviews.locations.ilike(f"%{search_location}%"))
    if min_rating is not None and max_rating is not None:
        query = query.filter(Reviews.rating.between(min_rating, max_rating))

    # Paginate the results
    entries = query.paginate(page=page, per_page=per_page)

    # Pass search terms back to the template to preserve state across pagination
    return render_template(
        "view_reviews.html",
        entries=entries,
        search_title=search_title,
        search_location=search_location,
        min_rating=min_rating,
        max_rating=max_rating,
    )


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    job_listings = fetch_job_listings()
    return jsonify(job_listings)
