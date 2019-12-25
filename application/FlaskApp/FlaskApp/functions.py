import PIL.Image
from flask import request, redirect, url_for, flash
from flask_login import current_user, login_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from .models import db, User, Category, Image, Thumbnail, Listing, Book

# This class serves as a helper to routing.py by providing functions for registration/authentication and
# creating listings from posted forms. In addition, this class also implements lazy registration for both
# selling and buying on the project pages.

class RouteFunctions:

    @staticmethod
    def authenticate():
        return True if current_user.is_authenticated else False

    # Function will return code for correct 'POST' method
    @staticmethod
    def post_routing():
        if request.form['btn'] == 'login':
            return RouteFunctions.userlogin()
        if request.form['btn'] == 'reg':
            return RouteFunctions.register()

    # Function will register user from form and log them in
    @staticmethod
    def register():
        user_pw = request.form['psw']
        user_pw2 = request.form['psw-repeat']
        # Test if password fields match
        if user_pw != user_pw2:
            # If password mismatch, redirect with error
            flash("Passwords must match", 'error')
            return redirect(url_for('register',
                                    listing=request.args.get('listing'),
                                    buying=request.args.get('buying')))

        # Try to insert new user to database
        try:
            user_email = request.form['email']
            user_name = request.form['username']
            User.add(user_pw, user_name, user_email)
            db.session.commit()
        # If email already in use, redirect with error
        except IntegrityError:
            flash("Email is already in use.", 'error')
            return redirect(url_for('register',
                                    listing=request.args.get('listing'),
                                    buying=request.args.get('buying')))

        # Log user in after registration
        RouteFunctions._login(user_email, user_pw, False)

        # If user registering after posting a listing
        if request.args.get('listing'):
            # Get listing from id and update seller column
            lid = request.args.get('listing')
            listing = Listing.query.get(lid)

            # Prevent listing.seller from being changed via url manipulation
            if not listing.seller:
                listing.seller = User.query.get(current_user.get_id())
                db.session.commit()
                flash("Thank you for registering!", 'reg')
                return redirect(url_for('listingpage', lid=lid))
        # If user registering after attempting to buy a listing
        elif request.args.get('buying'):
            lid = request.args.get('buying')
            RouteFunctions.purchase_listing(lid)
            # Redirect to purchased listing
            return redirect(url_for('listingpage', lid=lid))

        # Redirect to successful registration page
        flash("Thank you for registering!", 'reg')
        return redirect(url_for('regpage'))

    # Log in user from form and return to homepage
    @staticmethod
    def userlogin():
        user_email = request.form['email']
        user_pw = request.form['Password']
        remember = True if request.form.get('remember') else False
        # Because 'remember' only exists if the button is checked an error is thrown
        # with request.form['remember'] when the button is unchecked

        # Website will redirect to home page after login
        success = RouteFunctions._login(user_email, user_pw, remember)
        if success:
            return redirect(request.url)
        else:
            return redirect(url_for('login'))

    # Login user from given credentials
    @staticmethod
    def _login(email, pw, rmb):
        user = User.query.filter_by(email=email).first()
        # Check that user exists and password matches
        if not user:
            flash("Email not found.", 'error')
            return False
        elif not check_password_hash(user.password, pw):
            flash("Invalid credentials.", 'error')
            return False
        login_user(user, remember=rmb)
        return True

    # Function will attempt to purchase listing from user
    @staticmethod
    def purchase_listing(lid):
        buy = Listing.buy_listing(lid)
        if buy:
            # Successful buy
            listing = Listing.get_listing(lid)
            sellmessage = "Thank you for purchasing: {}".format(listing.title)
            flash(sellmessage, 'reg')
        else:
            # Already purchased
            flash('Could not complete your purchase.', 'reg')

    @staticmethod
    def create_listing(heading):
        # Get arguments from form
        title = request.form['title']
        category_ID = Category.get_category(heading).id
        description = request.form['description']
        sell_price = request.form['sell_price']
        upload = request.files['image']

        listing = Listing(title=title,
                          description=description,
                          sell_price=sell_price,
                          category_id=category_ID)

        # If user logged in, set seller
        if RouteFunctions.authenticate():
            listing.seller = User.query.get(current_user.get_id())
        # If images uploaded, update image
        if upload:
            listing = RouteFunctions.create_images(listing)

        db.session.add(listing)
        if heading != 'Books':
            db.session.commit()
            return listing.id
        else:
            # If listing is for books, update book entry with form values
            dept = request.form['course_name']
            course = request.form['course_number']

            book = Book(dept=dept,
                        course=course)
            book.listing = listing

            db.session.add(book)
            db.session.commit()
            return book.id

    @staticmethod
    def create_images(listing):
        # Read image from form
        upload = PIL.Image.open(request.files['image'])
        upload.thumbnail((1000, 1000))
        # Regular image
        img = Image(image=upload.tobytes(),
                    mode=upload.mode,
                    size=str(upload.size),
                    format=upload.format)

        upload.thumbnail((250, 250))
        # Thumbnail image
        thumb = Thumbnail(thumbnail=upload.tobytes(),
                          mode=upload.mode,
                          size=str(upload.size),
                          format=upload.format)

        # one to many; uselist=True
        listing.images.append(img)
        listing.thumbnails.append(thumb)
        # one to one; uselist=False
        img.thumbnail = thumb

        # cascade=save-update
        # when added, associated relationships (EG listing.images.append(img)) will be pulled in
        # see: https://docs.sqlalchemy.org/en/13/orm/cascades.html
        return listing
