from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Not encrypted for prototype
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with listings
    listings = db.relationship('Listing', backref='creator', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    assistance_type = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    premium_duration = db.Column(db.Integer, nullable=True)  # Duration in days (1, 3, 7, 30)
    premium_expires_at = db.Column(db.DateTime, nullable=True)  # When premium status expires
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Listing {self.name}>'
    
    def is_premium_active(self):
        """Check if premium status is still active"""
        if not self.is_premium or not self.premium_expires_at:
            return False
        return datetime.utcnow() < self.premium_expires_at
    
    def get_premium_status_display(self):
        """Return status for display purposes"""
        if not self.is_premium:
            return "Regular"
        
        if self.is_premium_active():
            days_left = (self.premium_expires_at - datetime.utcnow()).days
            return f"Premium (expires in {days_left+1} days)"
        else:
            return "Premium (expired)"
            
    def set_premium_duration(self, days):
        """Set premium status with expiration date"""
        self.is_premium = True
        self.premium_duration = days
        self.premium_expires_at = datetime.utcnow() + timedelta(days=days)
        
    @classmethod
    def get_active_premium_listings(cls):
        """Get all active premium listings"""
        now = datetime.utcnow()
        return cls.query.filter(
            cls.is_premium == True,
            cls.premium_expires_at > now
        ).order_by(cls.created_at.desc()).all()
        
    @classmethod
    def get_non_premium_or_expired_listings(cls):
        """Get all non-premium or expired premium listings"""
        now = datetime.utcnow()
        return cls.query.filter(
            db.or_(
                cls.is_premium == False,
                db.and_(
                    cls.is_premium == True,
                    cls.premium_expires_at <= now
                )
            )
        ).order_by(cls.created_at.desc()).all()
