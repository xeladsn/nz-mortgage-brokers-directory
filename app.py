from flask import Flask, render_template, abort, request, jsonify, redirect, url_for, session, flash, send_from_directory, Response
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from functools import wraps
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure server name based on environment
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SERVER_NAME'] = 'kiwihomebuyers.com'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['ENV'] = 'production'
else:
    app.config['ENV'] = 'development'

# Route for About page
@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

# Mapping dictionaries for routes
specialty_routes = {
    'first-time-homebuyer': 'First time homebuyer',
    'damaged-credit': 'Damaged Credit',
    'refinancing-and-equity-release': 'Refinancing and Equity Release',
    'construction-new-build-loans': 'Construction/ New Build Loans',
    'non-resident-new-to-nz': 'Non-resident/ New to NZ',
    'high-net-worth': 'High Net-Worth',
    'low-income-govt-supported': 'Low Income / Government supported',
    'commercial-property': 'Commercial Property'
}

service_routes = {
    'kiwisaver': 'Kiwisaver',
    'cashback': 'Cashback',
    'self-employed': 'Self Employed',
    'property-investor': 'Property Investor',
    'commercial-loans': 'Commercial Loans',
    'construction-loans': 'Construction Loans',
    'low-deposit': '10% or less deposits',
    'kainga-ora-loan': 'Kāinga Ora Loan',
    'financial-advice': 'Financial Advice'
}

# Create reverse mappings for template use
reverse_specialty_routes = {v: k for k, v in specialty_routes.items()}
reverse_service_routes = {v: k for k, v in service_routes.items()}

# Make mappings available in templates
@app.context_processor
def utility_processor():
    return {
        'specialty_routes': specialty_routes,
        'service_routes': service_routes,
        'reverse_specialty_routes': reverse_specialty_routes,
        'reverse_service_routes': reverse_service_routes,
        'show_filters': False  # Default to False, will be overridden in specific routes
    }

# Home route with filtering
@app.route('/')
def home():
    # Get filter parameters
    specialty_filters = request.args.get('specialties', '').split(',') if request.args.get('specialties') else []
    service_filters = request.args.get('services', '').split(',') if request.args.get('services') else []
    
    # Filter MAs based on selected criteria
    filtered_mas = mas
    
    if specialty_filters and specialty_filters[0]:  # Check if the list is not empty and not just an empty string
        # Convert route keys to display names for comparison with MA tags
        specialty_names = [specialty_routes[route] for route in specialty_filters if route in specialty_routes]
        if specialty_names:
            filtered_mas = [ma for ma in filtered_mas if any(tag in specialty_names for tag in ma['tags'])]
    
    if service_filters and service_filters[0]:  # Check if the list is not empty and not just an empty string
        # Convert route keys to display names for comparison with MA services
        service_names = [service_routes[route] for route in service_filters if route in service_routes]
        if service_names:
            filtered_mas = [ma for ma in filtered_mas if any(service in service_names for service in ma['services'])]
    
    # Make sure each MA has a services list for client-side filtering
    for ma in filtered_mas:
        if 'services' not in ma:
            ma['services'] = []
    
    return render_template('home.html', 
                          mas=filtered_mas, 
                          specialty_routes=specialty_routes, 
                          service_routes=service_routes,
                          show_filters=True)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# Admin credentials (in production, use hashed passwords and store securely)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Secret key for session
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Admin login required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', blog_posts=blog_posts)

@app.route('/admin/blog/create', methods=['GET', 'POST'])
@admin_required
def admin_blog_create():
    if request.method == 'POST':
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            image_path = save_uploaded_file(file)
            if not image_path and file.filename:
                flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')
                return redirect(request.url)
        
        new_post = {
            'id': len(blog_posts) + 1,
            'title': request.form['title'],
            'content': request.form['content'],
            'author': request.form['author'],
            'date': request.form['date'],
            'image': image_path if image_path else None
        }
        blog_posts.append(new_post)
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/blog_form.html')

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(post_id):
    post = next((post for post in blog_posts if post['id'] == post_id), None)
    if not post:
        abort(404)
    
    if request.method == 'POST':
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:  # New file was selected
                # Delete old image if it exists
                if post['image']:
                    old_image_path = os.path.join(app.root_path, 'static', post['image'])
                    try:
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    except Exception as e:
                        print(f"Error deleting old image: {e}")
                
                # Save new image
                image_path = save_uploaded_file(file)
                if image_path:
                    post['image'] = image_path
                else:
                    flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')
                    return redirect(request.url)
        
        post['title'] = request.form['title']
        post['content'] = request.form['content']
        post['author'] = request.form['author']
        post['date'] = request.form['date']
        
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/blog_form.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
@admin_required
def admin_blog_delete(post_id):
    global blog_posts
    post = next((post for post in blog_posts if post['id'] == post_id), None)
    
    if post and post['image']:
        # Delete associated image file
        image_path = os.path.join(app.root_path, 'static', post['image'])
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image: {e}")
    
    blog_posts = [p for p in blog_posts if p['id'] != post_id]
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# File upload configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'blog_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        # Return relative path for database storage
        return f"blog_images/{new_filename}"
    return None

# Routes for robots.txt and sitemap.xml
@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    root = ET.Element('urlset')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Determine the base URL
    if os.environ.get('FLASK_ENV') == 'production':
        base_url = 'https://kiwihomebuyers.com'
    else:
        base_url = request.url_root.rstrip('/')
    
    # Add static pages
    pages = [
        {'loc': f"{base_url}/", 'priority': '1.0'},
        {'loc': f"{base_url}/blog", 'priority': '0.8'},
    ]
    
    # Add specialty pages
    for route in specialty_routes.keys():
        pages.append({
            'loc': f"{base_url}/specialty/{route}",
            'priority': '0.7'
        })
    
    # Add MA detail pages
    for ma in mas:
        pages.append({
            'loc': f"{base_url}/ma/{ma['id']}",
            'priority': '0.6'
        })
    
    # Add blog posts
    for post in blog_posts:
        pages.append({
            'loc': f"{base_url}/blog/{post['id']}",
            'lastmod': post.get('date', datetime.now().strftime('%Y-%m-%d')),
            'priority': '0.6'
        })
    
    # Create XML structure
    for page in pages:
        url = ET.SubElement(root, 'url')
        loc = ET.SubElement(url, 'loc')
        loc.text = page['loc']
        
        if 'lastmod' in page:
            lastmod = ET.SubElement(url, 'lastmod')
            lastmod.text = page['lastmod']
        
        if 'priority' in page:
            priority = ET.SubElement(url, 'priority')
            priority.text = page['priority']
    
    # Create the XML string
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    
    return Response(xml_declaration + xml_str, mimetype='application/xml')

# Mock data for MAs
mas = [
    {
        "id": 1,
        "name": "Sarah Johnson",
        "profile_picture": "profile_pics/sarah_johnson.jpg",
        "company": "Mortgage Labs",
        "type": "First Home Specialist",
        "description": "Expert mortgage brokering services for first-time homebuyers, helping Kiwis get on the property ladder with ease.",
        "detailed_description": "With over 15 years of experience in the mortgage industry, Sarah specializes in helping first-time homebuyers navigate the complex process of purchasing their first property. She has extensive knowledge of government assistance programs, including KiwiSaver withdrawals and First Home Grants. Sarah takes pride in providing personalized guidance, breaking down complex financial terms, and finding the best mortgage solutions tailored to each client's unique situation. Her approach combines thorough market knowledge with a genuine commitment to helping Kiwis achieve their homeownership dreams.",
        "nationwide": True,
        "location": "Wellington",
        "years_experience": 15,
        "online_capable": True,
        "supported_institutions": ["ANZ", "ASB", "BNZ", "Westpac", "Kiwibank"],
        "tags": ["First time homebuyer", "Low Income / Government supported"],
        "services": [
            "Kiwisaver",
            "Self Employed",
            "10% or less deposits",
            "Kāinga Ora Loan"
        ],
        "endorsements": [
            {
                "name": "Emma Thompson",
                "date": "May 9, 2024",
                "comment": "Sarah made my first home buying experience a breeze. Her knowledge of first home buyer schemes was invaluable.",
                "title": "Marketing Manager at Wellington Tech",
                "picture": "endorsements_faces/emma_thompson.jpg"
            },
            {
                "name": "John Smith",
                "date": "June 4, 2024",
                "comment": "Great service and very professional.",
                "title": "Engineer at Auckland Engineering",
                "picture": "endorsements_faces/john_smith.jpg"
            }
        ]
    },
    {
        "id": 2,
        "name": "Michael Chen",
        "profile_picture": "profile_pics/michael_chen.jpg",
        "company": "Home Finance Direct",
        "type": "Investment Property Specialist",
        "description": "A long-term partner for property investors looking to expand their portfolio across New Zealand...",
        "detailed_description": "Michael brings a wealth of experience in investment property financing, with a particular focus on commercial and residential property portfolios. His expertise extends to complex financing structures, including trust arrangements and company setups. Having worked with numerous successful property investors, Michael understands the importance of strategic financial planning and can provide valuable insights into market trends and investment opportunities. He maintains strong relationships with major banks and alternative lenders, ensuring his clients get the most competitive rates and terms for their investment properties.",
        "nationwide": True,
        "location": "Auckland",
        "years_experience": 12,
        "online_capable": True,
        "supported_institutions": ["ANZ", "ASB", "BNZ", "Westpac", "SBS Bank", "Liberty Financial"],
        "tags": ["Commercial Property", "High Net-Worth"],
        "services": [
            "Cashback",
            "Property Investor",
            "Commercial Loans",
            "Financial Advice"
        ],
        "endorsements": [
            {
                "name": "David Wilson",
                "date": "Jun 17, 2024",
                "comment": "Michael has been crucial in growing my property portfolio. His market insights and negotiation skills with lenders are top-notch.",
                "title": "Director at Auckland Property Developments",
                "picture": "endorsements_faces/david_wilson.jpg"
            },
            {
                "name": "Jane Doe",
                "date": "July 1, 2024",
                "comment": "Very knowledgeable and helpful.",
                "title": "Investor at Wellington Investments",
                "picture": "endorsements_faces/jane_doe.jpg"
            }
        ]
    },
    {
        "id": 3,
        "name": "Emily Patel",
        "profile_picture": "profile_pics/emily_patel.jpg",
        "company": "Property Finance Partners",
        "type": "Self-Employed Mortgage Specialist",
        "description": "Emily is the go-to mortgage broker for self-employed Kiwis and small business owners seeking home loans...",
        "detailed_description": "Emily has carved out a niche in helping self-employed individuals and business owners secure home loans. Understanding the unique challenges faced by self-employed borrowers, she excels at presenting complex income structures to lenders in a favorable light. Her background in accounting combined with mortgage broking expertise allows her to effectively analyze business financials and identify the best lending solutions. Emily stays up-to-date with changing lending policies and maintains strong relationships with lenders who are more flexible with self-employed applications.",
        "nationwide": True,
        "location": "Christchurch",
        "years_experience": 8,
        "online_capable": True,
        "supported_institutions": ["ANZ", "ASB", "BNZ", "Westpac", "Co-operative Bank", "NZCU"],
        "tags": ["Damaged Credit", "Refinancing and Equity Release"],
        "services": [
            "Kiwisaver",
            "Self Employed",
            "Construction Loans",
            "10% or less deposits"
        ],
        "endorsements": [
            {
                "name": "Sophie Wilson",
                "date": "May 2, 2024",
                "comment": "As a freelancer, I thought getting a mortgage would be impossible. Emily not only made it possible but made the whole process smooth and stress-free.",
                "title": "Freelance Graphic Designer",
                "picture": "endorsements_faces/sophie_wilson.jpg"
            },
            {
                "name": "David Brown",
                "date": "June 20, 2024",
                "comment": "Excellent service and support.",
                "title": "Small Business Owner",
                "picture": "endorsements_faces/david_brown.jpg"
            }
        ]
    },
    {
        "id": 4,
        "name": "James Tait",
        "profile_picture": "profile_pics/james_tait.jpg",
        "company": "NZ Mortgages Ltd",
        "type": "Full-Service Mortgage Broker",
        "description": "James provides comprehensive mortgage solutions for all types of borrowers across New Zealand, from first-time buyers to seasoned investors.",
        "detailed_description": "With a career spanning two decades in the New Zealand mortgage industry, James has developed expertise across all aspects of property finance. His comprehensive approach involves understanding not just the immediate lending needs but also the long-term financial goals of his clients. James is particularly skilled in handling complex cases, including non-resident applications and commercial property financing. He has built strong relationships with multiple lenders and can often secure approvals for cases that other brokers find challenging. His extensive network and deep understanding of various lending policies make him a valuable partner for any property financing need.",
        "nationwide": True,
        "location": "Hamilton",
        "years_experience": 20,
        "online_capable": True,
        "supported_institutions": ["ANZ", "ASB", "BNZ", "Westpac", "Kiwibank", "TSB", "Resimac", "Pepper Money"],
        "tags": ["First time homebuyer", "Non-resident/ New to NZ", "Commercial Property"],
        "services": [
            "Cashback",
            "Property Investor",
            "Commercial Loans",
            "Kāinga Ora Loan",
            "Financial Advice"
        ],
        "endorsements": [
            {
                "name": "Robert Clark",
                "date": "Apr 10, 2024",
                "comment": "James has been my go-to for all things property finance. His expertise across different loan types and lenders is unmatched.",
                "title": "CEO of Christchurch Retail Group",
                "picture": "endorsements_faces/robert_clark.jpg"
            },
            {
                "name": "Laura White",
                "date": "July 15, 2024",
                "comment": "Very efficient and reliable.",
                "title": "Real Estate Agent",
                "picture": "endorsements_faces/laura_white.jpg"
            }
        ]
    },
    {
        "id": 5,
        "name": "Rustam Nomozov",
        "profile_picture": "profile_pics/rustam_nomozov.png",
        "company": "Mortgage Labs",
        "type": "Family Finance Doctor",
        "description": "\"Family Finance Doctor\" - Focused on treating client's challenge like they're my own, finding solutions that others overlook.",
        "detailed_description": "With over a decade in finance, I work on guiding first-time buyers, business owners, and investors on their property journeys. Whether you're searching for your next home or expanding your property portfolio, my experience in property trading and development—coupled with active involvement in the Wellington Property Investment Association—ensures a smooth and rewarding experience. I'm passionate about real estate and ready to help you unlock new opportunities.",
        "nationwide": True,
        "location": "Wellington",
        "years_experience": 12,
        "online_capable": True,
        "supported_institutions": ["BNZ", "ANZ"],
        "tags": ["First time homebuyer", "Refinancing and Equity Release", "Commercial Property"],
        "services": [
            "Property Investor",
            "Financial Advice",
            "Self Employed"
        ],
        "endorsements": [
            {
                "name": "Client Testimonial",
                "date": "July 15, 2024",
                "comment": "Thanks to Rustam, we were able to restructure our mortgage allowing us to stay in our dream home and come up with the funds for our second home",
                "title": "Satisfied Client",
                "picture": "endorsements_faces/emma_wilson.jpg"
            },
            {
                "name": "David Wilson",
                "date": "June 22, 2024",
                "comment": "Rustam helped us navigate the complex process of buying our first investment property. His knowledge of the market was invaluable.",
                "title": "Property Investor",
                "picture": "endorsements_faces/david_wilson.jpg"
            },
            {
                "name": "Sarah Thompson",
                "date": "May 30, 2024",
                "comment": "As a business owner, I thought getting a mortgage would be difficult. Rustam made it simple and found me a great rate.",
                "title": "Small Business Owner",
                "picture": "endorsements_faces/sarah_thompson.jpg"
            },
            {
                "name": "Robert Clark",
                "date": "April 15, 2024",
                "comment": "Rustam's expertise in commercial property financing helped us expand our business locations. Highly recommended!",
                "title": "CEO of Wellington Retail",
                "picture": "endorsements_faces/robert_clark.jpg"
            },
            {
                "name": "Jane Doe",
                "date": "March 8, 2024",
                "comment": "First-time homebuyer here. Rustam explained everything clearly and found us options we didn't know existed.",
                "title": "Marketing Professional",
                "picture": "endorsements_faces/jane_doe.jpg"
            }
        ]
    }
]

# Sample blog posts
blog_posts = [
    {
        "id": 1,
        "title": "Understanding Mortgage Rates in 2024",
        "date": "2024-01-05",
        "summary": "A comprehensive guide to current mortgage rates and what they mean for homebuyers.",
        "content": """Understanding Mortgage Rates in 2024

Understanding mortgage rates is crucial for anyone looking to buy a home or refinance their existing mortgage. In 2024, several factors are influencing mortgage rates in New Zealand.

Economic Conditions:

• Current market trends
• Inflation rates
• Employment rates

Reserve Bank Policies:

• Official Cash Rate (OCR)
• Monetary policy decisions
• Banking regulations

Global Financial Markets:

• International economic conditions
• Foreign investment trends
• Currency exchange rates

What This Means for Homebuyers:

• Fixed vs. floating rates considerations
• How to get the best rates
• Timing your mortgage application

Contact a mortgage broker today to understand how these factors affect your specific situation.""",
        "author": "Sarah Johnson",
        "image": "blog_images/mortgage-rates.jpg"
    },
    {
        "id": 2,
        "title": "First-Time Home Buyer's Guide",
        "date": "2024-12-28",
        "summary": "Everything you need to know about buying your first home in New Zealand.",
        "content": """First-Time Home Buyer's Guide

Buying your first home is an exciting but complex journey. Here's what you need to know:

Getting Started:

• Assess your financial situation
• Save for a deposit
• Understand your borrowing capacity

Key Steps in the Process:

• Getting pre-approval
• House hunting
• Making an offer
• Legal requirements
• Settlement process

Government Assistance:

• First Home Grant
• First Home Loan
• KiwiSaver withdrawal

Tips for Success:

• Work with experienced professionals
• Do thorough research
• Don't rush the process

Remember, a mortgage broker can guide you through this journey and help you find the best loan options.""",
        "author": "Michael Chen",
        "image": "blog_images/first-time-buyer.jpg"
    },
    {
        "id": 3,
        "title": "How to Choose the Right Mortgage Broker",
        "date": "2024-12-20",
        "summary": "Tips for selecting the best mortgage broker for your needs.",
        "content": """How to Choose the Right Mortgage Broker

Choosing the right mortgage broker is crucial for your home buying success. Here's how to make the best choice:

Key Considerations:

• Experience and qualifications
• Range of lenders
• Communication style
• Client testimonials
• Specializations

Questions to Ask:

• How many lenders do you work with?
• What are your fees?
• Can you explain your process?
• What's your experience with similar cases?

Red Flags to Watch For:

• Pressure tactics
• Unrealistic promises
• Poor communication
• Lack of transparency

Remember to do your research and trust your instincts when choosing a mortgage broker.""",
        "author": "Emily Patel",
        "image": "blog_images/policy-changes.jpg"
    }
]

@app.route('/ma/<int:ma_id>')
def ma_detail(ma_id):
    ma = next((ma for ma in mas if ma['id'] == ma_id), None)
    if ma:
        return render_template('ma_detail.html', ma=ma)
    else:
        abort(404)

@app.route('/specialty/<type>')
def specialty(type):
    if type not in specialty_routes:
        abort(404)
    filtered_mas = [ma for ma in mas if specialty_routes[type] in ma['tags']]
    return render_template('home.html', mas=filtered_mas, title=f"Top {specialty_routes[type]} Expert Firms")

@app.route('/service/<type>')
def service(type):
    if type not in service_routes:
        abort(404)
    filtered_mas = [ma for ma in mas if service_routes[type] in ma['services']]
    return render_template('home.html', mas=filtered_mas, title=f"{service_routes[type]}")

@app.route('/blog')
def blog():
    return render_template('blog.html', title='Blog', posts=blog_posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = next((post for post in blog_posts if post['id'] == post_id), None)
    if post is None:
        abort(404)
    return render_template('blog_post.html', title=post['title'], post=post)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    ma_id = int(data.get('ma_id'))
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    loan_purpose = data.get('loan_purpose', '')
    household_income = data.get('household_income', '')
    purchase_location = data.get('purchase_location', '')
    deposit_amount = data.get('deposit_amount', '')
    deposit_sources = data.get('deposit_sources', [])
    additional_info = data.get('additional_info', '')

    # Validate required fields
    required_fields = {
        'name': name,
        'email': email,
        'phone': phone
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        return jsonify({
            'success': False, 
            'message': f'The following fields are required: {", ".join(missing_fields)}'
        }), 400

    # Find the MA by ID
    ma = next((ma for ma in mas if ma['id'] == ma_id), None)
    if not ma:
        return jsonify({'success': False, 'message': 'MA not found'}), 404

    # Construct the email message
    subject = f"New request for {ma['name']}"
    body = f"""
    You have a new contact request from {name}.

    Contact Information:
    Name: {name}
    Email: {email}
    Phone: {phone}

    Loan Details:
    Purpose: {loan_purpose if loan_purpose else 'Not provided'}
    Household Income: {household_income if household_income else 'Not provided'}
    Purchase Location: {purchase_location if purchase_location else 'Not provided'}
    Deposit Amount: {deposit_amount if deposit_amount else 'Not provided'}
    Deposit Sources: {', '.join(deposit_sources) if deposit_sources else 'Not provided'}

    Additional Information:
    {additional_info if additional_info else 'None provided'}
    
    Please forward this message to {ma['name']} or the appropriate person for follow-up.
    """

    try:
        msg = Message(subject,
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[os.getenv("RECIPIENT_EMAIL")])
        msg.body = body

        mail.send(msg)
        print("Message sent successfully")
        return jsonify({'success': True, 'message': 'Message sent successfully'}), 200
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to send message'}), 500

@app.route('/send_quiz_message', methods=['POST'])
def send_quiz_message():
    try:
        data = request.get_json()
        
        # Create email message
        msg = Message(
            'New Quiz Submission',
            sender=app.config['MAIL_USERNAME'],
            recipients=[os.getenv('RECIPIENT_EMAIL')]
        )
        
        # Format the email body
        msg.body = f'''
New quiz submission received:

Contact Information:
------------------
Email: {data.get('email')}
First Name: {data.get('firstName')}
Last Name: {data.get('lastName')}

Homebuying Situation:
------------------
Situation: {data.get('situation')}
Investment Type: {data.get('investmentType') if data.get('situation') == 'investment' else 'N/A'}

Income Details:
------------------
Income Sources: {', '.join(data.get('income', []))}

Ownership Details:
------------------
Arrangement: {data.get('ownership')}

Financial Profile:
------------------
Profile: {data.get('profile')}
Mortgage Product Interest: {data.get('product')}
Down Payment Status: {data.get('downPayment')}

Priorities and Preferences:
------------------
Main Priority: {data.get('priority')}
Residency Status: {data.get('residency')}
'''
        
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)