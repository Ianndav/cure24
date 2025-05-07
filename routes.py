from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from models import User, Listing
from forms import RegistrationForm, LoginForm, ListingForm, PaymentForm
import logging
from datetime import datetime, timedelta
import os

def register_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html', title='Welcome to Cure24')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Register', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.password == form.password.data:
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Login unsuccessful. Please check email and password.', 'danger')
        
        return render_template('login.html', title='Login', form=form)
    
    @app.route('/logout')
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get updated listings with premium status checks
        listings = Listing.query.filter_by(user_id=current_user.id).all()
        
        # Check for expired premium listings
        now = datetime.utcnow()
        for listing in listings:
            if listing.is_premium and listing.premium_expires_at and listing.premium_expires_at <= now:
                # Premium has expired, but is_premium flag is still True
                # The listing will still show as premium but with "expired" status
                pass
                
        return render_template('dashboard.html', title='Dashboard', listings=listings)
    
    @app.route('/create-listing', methods=['GET', 'POST'])
    @login_required
    def create_listing():
        form = ListingForm()
        if form.validate_on_submit():
            # Create new listing
            listing = Listing(
                name=form.name.data,
                description=form.description.data,
                assistance_type=form.assistance_type.data,
                hourly_rate=form.hourly_rate.data,
                location=form.location.data,
                user_id=current_user.id
            )
            
            # Handle premium status
            if form.is_premium.data:
                premium_days = int(form.premium_duration.data)
                listing.set_premium_duration(premium_days)
                
                # Add listing to database
                db.session.add(listing)
                db.session.commit()
                
                # For now, skip payment (since we don't have Stripe integrated yet)
                # In a real environment, redirect to the payment page:
                # return redirect(url_for('premium_payment', listing_id=listing.id))
                
                flash(f'Your premium listing has been created! It will be promoted for {premium_days} days.', 'success')
            else:
                # Non-premium listing
                db.session.add(listing)
                db.session.commit()
                flash('Your listing has been created!', 'success')
                
            return redirect(url_for('dashboard'))
        
        return render_template('create_listing.html', title='Create Listing', form=form)
    
    @app.route('/premium-payment/<int:listing_id>', methods=['GET', 'POST'])
    @login_required
    def premium_payment(listing_id):
        """
        This route will be used for the payment process once Stripe is integrated.
        For now, it's a placeholder.
        """
        listing = Listing.query.get_or_404(listing_id)
        
        # Check if listing belongs to current user
        if listing.user_id != current_user.id:
            flash('You are not authorized to access this listing.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Calculate price based on duration
        prices = {
            1: 2.99,
            3: 7.99,
            7: 14.99,
            30: 39.99
        }
        
        amount = prices.get(listing.premium_duration, 0)
        
        form = PaymentForm(
            listing_id=listing.id,
            premium_duration=listing.premium_duration,
            amount=amount
        )
        
        if form.validate_on_submit():
            # Here we would process payment with Stripe
            # For now, we'll just show a success message
            flash(f'Payment of €{amount} completed successfully! Your listing is now premium.', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template(
            'premium_payment.html',
            title='Premium Payment',
            form=form,
            listing=listing,
            amount=amount
        )

    @app.route('/find-assistants')
    def find_assistants():
        # Get active premium listings (where premium hasn't expired)
        now = datetime.utcnow()
        
        # Get active premium listings
        premium_listings = Listing.query.filter(
            Listing.is_premium == True,
            Listing.premium_expires_at > now
        ).order_by(Listing.created_at.desc()).all()
        
        # Get non-premium or expired premium listings
        regular_listings = Listing.query.filter(
            db.or_(
                Listing.is_premium == False,
                db.and_(
                    Listing.is_premium == True,
                    db.or_(
                        Listing.premium_expires_at <= now,
                        Listing.premium_expires_at == None
                    )
                )
            )
        ).order_by(Listing.created_at.desc()).all()
        
        # Combine lists with active premium listings first
        all_listings = premium_listings + regular_listings
        
        return render_template('find_assistants.html', title='Find Healthcare Assistants', listings=all_listings)
    
    @app.route('/premium-pricing')
    def premium_pricing():
        """Return premium pricing information as JSON"""
        pricing = {
            "1": {"days": 1, "price": 2.99, "description": "1 day promotion"},
            "3": {"days": 3, "price": 7.99, "description": "3 days promotion"},
            "7": {"days": 7, "price": 14.99, "description": "7 days promotion"},
            "30": {"days": 30, "price": 39.99, "description": "30 days promotion"}
        }
        return jsonify(pricing)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', title='404 - Page Not Found'), 404
