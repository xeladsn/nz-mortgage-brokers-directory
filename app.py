from flask import Flask, render_template, abort, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

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
        'reverse_service_routes': reverse_service_routes
    }

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

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
    }
]

# Sample blog posts
blog_posts = [
    {
        "id": 1,
        "title": "Understanding Mortgage Rates in 2025",
        "date": "2025-01-05",
        "summary": "A comprehensive guide to current mortgage rates and what they mean for homebuyers.",
        "content": """Understanding Mortgage Rates in 2025

Understanding mortgage rates is crucial for anyone looking to buy a home or refinance their existing mortgage. In 2025, several factors are influencing mortgage rates in New Zealand.

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
        "image": "blog/mortgage-rates.jpg"
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
        "image": "blog/first-time-buyer.jpg"
    },
    {
        "id": 3,
        "title": "How to Choose the Right Mortgage Broker",
        "date": "2024-12-20",
        "summary": "Tips for selecting the best mortgage broker for your needs.",
        "content": """How to Choose the Right Mortgage Broker

Choosing the right mortgage broker is crucial for your home buying success. Here's how to make the best choice:

What to Look For:

• Experience and Qualifications
• Range of lender relationships
• Client testimonials
• Communication style

Questions to Ask:

• How many lenders do you work with?
• What are your fees?
• What's your process?
• How do you handle challenges?

Red Flags to Watch For:

• Pressure tactics
• Lack of transparency
• Poor communication
• Limited lender options

Making Your Decision:

• Compare multiple brokers
• Check references
• Trust your instincts

Take time to find the right broker who understands your needs and can guide you effectively.""",
        "author": "Emily Patel",
        "image": "blog/policy-changes.jpg"
    }
]

@app.route('/')
def home():
    return render_template('home.html', mas=mas, title="Find the best mortgage brokers in NZ")

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