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

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    ma_id = int(data.get('ma_id'))
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    profession = data.get('profession')
    household_income = data.get('household_income')

    # Find the MA by ID
    ma = next((ma for ma in mas if ma['id'] == ma_id), None)
    if not ma:
        return jsonify({'success': False, 'message': 'MA not found'}), 404

    # Construct the email message
    subject = f"New request for {ma['name']}"
    body = f"""
    You have a new contact request from {first_name} {last_name}.

    Email: {email}
    Profession: {profession}
    Household Tax Income: {household_income}
    
    Please forward this message to the appropriate person at {ma['name']} for follow-up.
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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)