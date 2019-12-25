import os

from flask import render_template, request, url_for, redirect, flash, send_from_directory
from flask_login import login_required, logout_user, current_user
from jinja2 import UndefinedError

# Import Python files from project
from .functions import RouteFunctions
from .content_management import Content
from .models import Admin, Book, Category, Listing, Message, User

# This file/function contains the routing for all project pages

def appRoutes(app):
    CONTENT_DICT = Content()

    @app.route('/', methods=["GET", "POST"])
    def homepage():
        if request.method == "POST":
            return RouteFunctions.post_routing()
        if current_user.is_authenticated:
            # Do logged-in page
            # Get user id
            userid = current_user.get_id()
            name = User.get_name(userid)

            searchResults = Listing.get_results('', 'All').all()
            searchResults.reverse()
            return render_template("home.html",
                                   title="Gator Joe's - Home",
                                   CONTENT_DICT=CONTENT_DICT,
                                   results=searchResults[:12],
                                   name=name)
        else:
            # User is not logged in
            # SearchResults fetches all the posted listings and passes 12 most recent postings
            searchResults = Listing.get_results('', 'All').all()
            searchResults.reverse()
            return render_template("home.html",
                                   title="Gator Joe's - Home",
                                   CONTENT_DICT=CONTENT_DICT,
                                   results=searchResults[:12])

    @app.route('/buytextbooks', methods=["GET", "POST"])
    def buybooks():
        if request.method == "POST":
            if request.form['btn'] == 'booksearch':
                course_name = request.form['course_name']
                course_number = request.form['course_number']
                results = Book.get_by_course(course_name, course_number)
                searchterm = course_name + course_number
                return render_template("listings/results.html",
                                       title="Gator Joe's - {} results".format(searchterm),
                                       CONTENT_DICT=CONTENT_DICT,
                                       searchcat='Books',
                                       searchquery=searchterm,
                                       num_results=len(results),
                                       results=results)
            else:
                return RouteFunctions.post_routing()
        return render_template("listings/buybooks.html",
                               title="Buy Textbooks",
                               CONTENT_DICT=CONTENT_DICT)

    @app.route('/mylistings', methods=["GET", "POST"])
    @login_required
    def mylistings():
        if request.method == "POST":
            return RouteFunctions.post_routing()
        else:
            userid = current_user.get_id()
            listings = User.get_user_listings(userid)
            if not listings:
                flash("You have no current listings.", 'reg')
                return redirect(url_for('homepage'))
            return render_template("listings/mylistings.html",
                                   title="Gator Joe's - My Listings",
                                   CONTENT_DICT=CONTENT_DICT,
                                   mylistings=listings)

    @app.route('/listing/<int:lid>', methods=["GET", "POST"])
    def listingpage(lid):
        if request.method == "POST":
            if request.form['btn'] == 'buy':
                # If user is not logged in, redirect to register page
                if not RouteFunctions.authenticate():
                    flash("Please register before making a purchase", 'reg')
                    return redirect(url_for('register', buying=lid))

                RouteFunctions.purchase_listing(lid)
                # Redirect to self, this time with method=GET
                return redirect(url_for('listingpage', lid=lid))
            else:
                return RouteFunctions.post_routing()
        else:
            listing = Listing.get_listing(lid)
            similar = Listing.get_results('', listing.category.name).all()
            return render_template("listings/listing.html",
                                   title="Gator Joe's - {}".format(listing.title),
                                   CONTENT_DICT=CONTENT_DICT,
                                   listing=listing,
                                   similar=similar[:4])

    @app.route('/sell/<string:heading>', methods=['GET', 'POST'])
    def sellitem(heading):
        itemcat = Category.get_category(heading)
        if itemcat:  # If url for is valid selling category
            if request.method == "POST":
                if request.form['btn'] == 'sell':
                    # Function will create listing from form info
                    lid = RouteFunctions.create_listing(heading)

                    # If user is not logged in, redirect to register page
                    if not RouteFunctions.authenticate():
                        flash("Please register before posting a listing", 'reg')
                        return redirect(url_for('register', listing=lid))

                    return redirect(url_for('homepage'))
                else:
                    return RouteFunctions.post_routing()
            else:
                if heading == 'Books':
                    return render_template('sell/sellbook.html',
                                           title="Gator Joe's - Post a textbook",
                                           CONTENT_DICT=CONTENT_DICT,
                                           heading=heading)
                else:
                    return render_template('sell/sellgeneral.html',
                                           title="Gator Joe's - Post a listing",
                                           CONTENT_DICT=CONTENT_DICT,
                                           heading=heading)

        else:
            # If url entered does not exist, redirect to 404
            return redirect(url_for('errorpage'))

    @app.route('/admin', methods=["GET", "POST"])
    @login_required
    def adminpage():
        # Check if user is admin
        if Admin.exists():
            listing = Listing.get_unapproved_listing()
            # checks if there are any unapproved listings recieved
            if listing is not None:
                if request.method == "POST":
                    lid = listing.id
                    # different responses for allow and deny buttons
                    if request.form['btn'] == "Allow":
                        Listing.approve_listing(lid)
                        return redirect(url_for('adminpage'))
                    elif request.form['btn'] == "Deny":
                        Listing.delete_listing(lid)
                        return redirect(url_for('adminpage'))
                    else:
                        return RouteFunctions.post_routing()
                else:
                    return render_template("admin.html",
                                           title="Gator Joe's - Administration",
                                           CONTENT_DICT=CONTENT_DICT,
                                           listing=listing)
            else:
                # If admin has no unapproved listing to check through
                flash("You are all caught up for the day", "reg")
                return redirect(url_for('homepage'))
        else:
            # If user not an admin, redirect to error page
            return redirect(url_for('error'))

    @app.route('/message/<int:lid>', methods=["GET", "POST"])
    @login_required
    def messagepage(lid):
        if request.method == 'POST':
            # once pressed send. get message from database
            if request.form['btn'] == 'send':
                listing = Listing.get_listing(lid)
                user = current_user
                sender = Message.sender
                temp = request.form['message']
                Message.send(lid, current_user.get_id(), temp)
                message = Message.get_listing_msgs(lid, current_user.get_id())
                return render_template("messages/message.html",
                                       title="Gator Joe's - Send a Message",
                                       CONTENT_DICT=CONTENT_DICT,
                                       sender=sender,
                                       user=user,
                                       message=message,
                                       listing=listing,
                                       category=listing.category.name,
                                       seller=listing.seller)
            else:
                return RouteFunctions.post_routing()
        else:
            user = current_user
            sender = Message.sender
            listing = Listing.get_listing(lid)
            message = Message.get_listing_msgs(lid, current_user.get_id())
            return render_template("messages/message.html",
                                   title="Gator Joe's - Send a Message",
                                   CONTENT_DICT=CONTENT_DICT,
                                   message=message,
                                   listing=listing,
                                   category=listing.category.name,
                                   seller=listing.seller)

    # This function serves as the message hub for a given user, it will show all message threads
    @app.route('/message', methods=["GET", "POST"])
    @login_required
    def messaging():
        userid = current_user.get_id()
        listings = Message.get_listing_user(userid)
        messages = []
        for lst in listings:
            lid = lst.listing_id
            listing = Listing.get_listing(lid)
            message = Message.get_last_msg(lid)
            messages.append((message, listing, listing.category.name, listing.seller))
        return render_template("messages/messagehub.html",
                               title="Gator Joe's - Messages",
                               CONTENT_DICT=CONTENT_DICT,
                               message=messages)

    @app.route('/results', methods=["GET", "POST"])
    def results():
        if request.method == 'POST':
            if request.form['btn'] == 'search':
                searchTerm = request.form['search']
                cat = request.form['category']
                searchResults = Listing.get_results(searchTerm, cat).all()

                return render_template("listings/results.html",
                                       title="Gator Joe's - {} results".format(searchTerm),
                                       CONTENT_DICT=CONTENT_DICT,
                                       auth=current_user.is_authenticated,
                                       searchquery=searchTerm, searchcat=cat, results=searchResults,
                                       num_results=len(searchResults))
            else:
                return RouteFunctions.post_routing()
        elif request.args:
            searchTerm = request.args.get('search')
            cat = request.args.get('cat')
            sort = request.args.get('sort')
            if sort == 'des':
                searchResults = Listing.get_sorted_results(searchTerm, cat, True).all()
            elif sort == 'asc':
                searchResults = Listing.get_sorted_results(searchTerm, cat, False).all()
            else:
                searchResults = Listing.get_results(searchTerm, cat).all()

            return render_template("listings/results.html",
                                   title="Gator Joe's - {} results".format(searchTerm),
                                   CONTENT_DICT=CONTENT_DICT,
                                   auth=current_user.is_authenticated,
                                   searchquery=searchTerm, searchcat=cat, results=searchResults,
                                   num_results=len(searchResults))
        else:
            return redirect(url_for('homepage'))

    # This page will routed to when an unregistered user tries to access a site that needs login
    @app.route('/login', methods=["GET", "POST"])
    def login():
        if RouteFunctions.authenticate():
            return redirect(url_for('homepage'))
        else:
            if request.method == "POST":
                return RouteFunctions.post_routing()
            else:
                return render_template("users/loginpage.html",
                                       title="Gator Joe's - Login",
                                       CONTENT_DICT=CONTENT_DICT,
                                       error=request.args.get('error'))

    @app.route('/logout', methods=["GET", "POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('homepage'))

    @app.route('/register', methods=["GET", "POST"])
    def register():
        if RouteFunctions.authenticate():
            # If logged in user tries to access register page
            return redirect(url_for('homepage'))
        else:
            if request.method == "POST":
                return RouteFunctions.post_routing()
            else:
                # Pass listing if given, will pass None if no arg passed
                return render_template("users/register.html",
                                       title="Gator Joe's - Register",
                                       CONTENT_DICT=CONTENT_DICT,
                                       listing=request.args.get('listing'),
                                       buying=request.args.get('buying'))

    @app.route('/about', methods=["GET", "POST"])
    def aboutpage():
        if request.method == "POST":
            return RouteFunctions.post_routing()
        return render_template("members/about.html",
                               title="Gator Joe's - Meet Our Team",
                               CONTENT_DICT=CONTENT_DICT,
                               iter=iter, next=next)

    @app.route('/about/<string:team_member>', methods=["GET", "POST"])
    def memberpage(team_member):
        if request.method == "POST":
            return RouteFunctions.post_routing()
        try:
            return render_template("members/member.html",
                                   CONTENT_DICT=CONTENT_DICT,
                                   team_member=team_member)
        except UndefinedError:
            # If url entered does not exist, redirect to 404
            return redirect(url_for('errorpage'))

    @app.route('/terms', methods=["GET", "POST"])
    def termprivacy():
        if request.method == "POST":
            return RouteFunctions.post_routing()
        return render_template("users/termprivacy.html",
                               title="Gator Joe's - Terms of Service",
                               CONTENT_DICT=CONTENT_DICT)

    @app.route('/error', methods=["GET", "POST"])
    def errorpage():
        if request.method == "POST":
            return RouteFunctions.post_routing()
        else:
            return render_template("pagenotfound.html",
                                   title="Gator Joe's - Page not found",
                                   CONTENT_DICT=CONTENT_DICT)

    @app.route('/forgot', methods=["GET", "POST"])
    def forgotpw():
        if RouteFunctions.authenticate():
            return redirect(url_for('homepage'))
        elif request.method == "POST":
            if request.form['btn'] == 'reset':
                return redirect(url_for('homepage'))
            return RouteFunctions.post_routing()
        else:
            return render_template("users/forgetpsw.html",
                                   title="Gator Joe's - Forgot Password",
                                   CONTENT_DICT=CONTENT_DICT)

    @app.route('/registered', methods=["GET", "POST"])
    def regpage():
        if request.method == "POST":
            return RouteFunctions.post_routing()
        else:
            return render_template("users/registered.html",
                                   title="Thank you for registering!",
                                   CONTENT_DICT=CONTENT_DICT)

    # This route will return the picture for project icon to be displayed in browser tabs
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')
