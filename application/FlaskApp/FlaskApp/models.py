import PIL.Image
import io
from ast import literal_eval
from base64 import b64encode
from flask_login import UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

# This file sets up the database schema for the project's development server. When called from __init__.py,
# these classes will create the schema directly into MySQL and avoids manually coding and editing table schemas.
# Each table (class) also contains relevant functions with which routing and templates access the database.

class Admin(db.Model):
    id = db.Column("admin_ID", None, db.ForeignKey("user.user_ID"), primary_key=True)

    user = db.relationship("User", uselist=False, cascade="save-update, merge")

    @staticmethod
    def exists():
        admin = Admin.query.get(current_user.get_id())
        return True if admin else False


class Book(db.Model):
    id = db.Column("book_ID", None, db.ForeignKey("listing.listing_ID"), primary_key=True)
    dept = db.Column("dept", db.String(5), unique=False, nullable=True)
    course = db.Column("course", db.Integer, unique=False, nullable=True)

    listing = db.relationship("Listing", uselist=False, single_parent=True, cascade="all, delete-orphan")

    @staticmethod
    def is_book(lid):
        book = Book.query.get(lid)
        return book if book else False

    @staticmethod
    def get_by_course(course_name, course_number):
        # This is a join of two tables Listing and Books
        # It will combine the tables and query them as single entries with Listing as the main table
        course_number = "%{}%".format(course_number)
        return Listing.query.join(Book, Book.id == Listing.id). \
            filter(and_(Book.dept == course_name, Book.course.like(course_number))). \
            filter(and_(Listing.approved, Listing.sold == False)).all()


class Category(db.Model):
    id = db.Column("category_ID", db.Integer, primary_key=True)
    name = db.Column("category_name", db.String(45), unique=True, nullable=False)

    @staticmethod
    def get_category(category_name):
        return Category.query.filter_by(name=category_name).first()

    @staticmethod
    def get_name(cat_id):
        return Category.query.get(cat_id).name

    @staticmethod
    def get_all_categories():
        return [row.name for row in Category.query.all()]


class Image(db.Model):
    id = db.Column("image_ID", db.Integer, primary_key=True)
    listing_id = db.Column("listing_ID", None, db.ForeignKey("listing.listing_ID"), nullable=False, unique=False)
    image = db.Column("image", db.Binary(2 ** 24), nullable=True, unique=False)
    mode = db.Column("mode", db.String(5), nullable=False, unique=False)
    size = db.Column("size", db.String(12), nullable=False, unique=False)
    format = db.Column("format", db.String(5), nullable=False, unique=False)

    thumbnail = db.relationship("Thumbnail", back_populates="image", uselist=False, cascade="all, delete-orphan")
    listing = db.relationship("Listing", back_populates="images", uselist=False, cascade="save-update, merge")

    @staticmethod
    def get_image(listing_id):
        listingimg = Image.query.filter_by(listing_id=listing_id).first()
        return listingimg if listingimg else None

    def as_BytesIO(self):
        image = PIL.Image.frombytes(self.mode, literal_eval(self.size), self.image)
        bts = io.BytesIO()
        image.save(bts, self.format)
        return bts

    def as_b64(self):
        return b64encode(self.as_BytesIO().getvalue()).decode("utf-8")


class Listing(db.Model):
    id = db.Column("listing_ID", db.Integer, primary_key=True)
    title = db.Column("title", db.String(45), unique=False, nullable=False)
    description = db.Column("description", db.String(5000), unique=False, nullable=True)
    sell_price = db.Column("sell_price", db.DECIMAL(6, 2), unique=False, default=0.00)
    category_id = db.Column("category_ID", None, db.ForeignKey("category.category_ID"), nullable=False, unique=False)
    seller_id = db.Column("seller_ID", None, db.ForeignKey("user.user_ID"), nullable=True, unique=False)
    sold = db.Column("sold", db.Boolean, default=False)
    approved = db.Column("approved", db.Boolean, default=False)

    category = db.relationship("Category", uselist=False, cascade="save-update, merge")
    seller = db.relationship("User", uselist=False, cascade="save-update, merge")
    images = db.relationship("Image", back_populates="listing", uselist=True, cascade="all, delete-orphan")
    thumbnails = db.relationship("Thumbnail", back_populates="listing", uselist=True, cascade="all, delete-orphan")
    messages = db.relationship("Message", back_populates="listing", uselist=True, cascade="all, delete-orphan")

    @staticmethod
    def get_listing(listing_id):
        return Listing.query.get(listing_id)

    @staticmethod
    def get_results(search, category):
        # %LIKE% needs this format
        search = "%{}%".format(search)

        if category == 'All':
            return Listing.query.filter(and_(Listing.title.like(search), Listing.approved, Listing.sold == False))
        else:
            catId = Category.query.filter_by(name=category).first().id
            return Listing.query. \
                filter(Listing.title.like(search)).filter_by(category_id=catId). \
                filter(and_(Listing.approved, Listing.sold == False))

    @staticmethod
    def get_sorted_results(search, category, descending):
        results = Listing.get_results(search, category)
        if descending:
            return results.order_by(Listing.sell_price.desc())
        else:
            return results.order_by(Listing.sell_price.asc())

    @staticmethod
    def get_unapproved_listing():
        unapproved = Listing.query.filter(and_(Listing.seller, Listing.approved.is_(False))).first()
        return unapproved

    @staticmethod
    def approve_listing(listing_id):
        listing = Listing.query.get(listing_id)
        listing.approved = True
        db.session.commit()

    @staticmethod
    def delete_listing(listing_id):
        if Book.is_book(listing_id):
            listing = Book.query.get(listing_id)
        else:
            listing = Listing.query.get(listing_id)
        db.session.delete(listing)
        db.session.commit()

    @staticmethod
    def buy_listing(listing_id):
        listing = Listing.query.get(listing_id)
        if listing.sold:
            return False
        else:
            listing.sold = True
            db.session.commit()
            return True


class Message(db.Model):
    id = db.Column("message_ID", db.Integer, primary_key=True)
    sender_id = db.Column("sender_ID", None, db.ForeignKey("user.user_ID"), nullable=False, unique=False)
    listing_id = db.Column("listing_ID", None, db.ForeignKey("listing.listing_ID"), nullable=False, unique=False)
    receiver_id = db.Column("receiver_ID", None, db.ForeignKey("user.user_ID"), nullable=False, unique=False)
    msg_read = db.Column("msg_read", db.Boolean, default=False)
    msg_sent = db.Column("msg_sent", db.DateTime, default=db.func.now())
    message = db.Column("message", db.Text, nullable=False, unique=False)

    listing = db.relationship("Listing", back_populates="messages", uselist=False, cascade="save-update, merge")
    sender = db.relationship("User", back_populates="sent_messages", foreign_keys="Message.sender_id", uselist=False,
                             cascade="save-update, merge")
    receiver = db.relationship("User", back_populates="received_messages", foreign_keys="Message.receiver_id",
                               uselist=False, cascade="save-update, merge")

    @staticmethod
    def send(listing_id, sender_id, msg_text):
        receiver_id = Listing.query.get(listing_id).seller_id
        new_msg = Message(sender_id=sender_id,
                          listing_id=listing_id,
                          receiver_id=receiver_id,
                          message=msg_text)
        db.session.add(new_msg)
        db.session.commit()

    @staticmethod
    def get_message(message_id):
        return Message.query.get(message_id)

    @staticmethod
    def get_sender(sender_id):
        return User.query.get(sender_id)

    @staticmethod
    def get_listing_msgs(listing_id, user_id):
        return Message.query.filter_by(listing_id=listing_id).filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)).all()

    @staticmethod
    def get_last_msg(listing_id):
        return Message.query.filter_by(listing_id=listing_id).order_by(Message.id.desc()).limit(1)

    @staticmethod
    def get_listing_user(user_id):
        return db.session.query(Message.listing_id).filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)).distinct().all()


class Thumbnail(db.Model):
    id = db.Column("thumbnail_ID", None, db.ForeignKey("image.image_ID"), primary_key=True)
    listing_id = db.Column("listing_ID", None, db.ForeignKey("listing.listing_ID"), nullable=False, unique=False)
    thumbnail = db.Column("image", db.Binary(2 ** 24), nullable=True, unique=False)
    mode = db.Column("mode", db.String(5), nullable=False, unique=False)
    size = db.Column("size", db.String(12), nullable=False, unique=False)
    format = db.Column("format", db.String(5), nullable=False, unique=False)

    image = db.relationship("Image", back_populates="thumbnail", uselist=False, single_parent=True,
                            cascade="all, delete-orphan")
    listing = db.relationship("Listing", back_populates="thumbnails", uselist=False, cascade="save-update, merge")

    @staticmethod
    def get_thumb(listing_id):
        listingthm = Thumbnail.query.filter_by(listing_id=listing_id).first()
        return listingthm if listingthm else False

    def as_BytesIO(self):
        image = PIL.Image.frombytes(self.mode, literal_eval(self.size), self.thumbnail)
        bts = io.BytesIO()
        image.save(bts, self.format)
        return bts

    def as_b64(self):
        return b64encode(self.as_BytesIO().getvalue()).decode("utf-8")


class User(db.Model, UserMixin):
    id = db.Column("user_ID", db.Integer, primary_key=True)
    name = db.Column("name", db.String(45), unique=False, nullable=False)
    email = db.Column("email", db.String(45), unique=True, nullable=False)
    password = db.Column("password", db.String(200), unique=True, nullable=False)

    sent_messages = db.relationship("Message", back_populates="sender", foreign_keys="Message.sender_id", uselist=True,
                                    cascade="save-update, merge")
    received_messages = db.relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id",
                                        uselist=True, cascade="save-update, merge")

    # noinspection PyArgumentList
    @staticmethod
    def add(nu_password: str, nu_name: str, nu_email: str):
        """
        Adds a new user to the database

        :param nu_email: email of the new user
        :param nu_password: password of the new user
        :param nu_name: full name of the new user
        :return: True fi successful, False otherwise
        """
        new_user = User(password=generate_password_hash(nu_password),
                        name=nu_name,
                        email=nu_email)
        db.session.add(new_user)
        db.session.commit()

    @staticmethod
    def get_name(user_id):
        return User.query.get(user_id).name

    @staticmethod
    def get_user_listings(user_id):
        return Listing.query.filter_by(seller_id=user_id).all()
