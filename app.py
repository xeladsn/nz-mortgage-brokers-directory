from flask import Flask, render_template, abort, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# Mock data for CPAs
cpas = [
    {
        "id": 1,
        "name": "Kiwi Home Loans",
        "type": "First Home Specialist",
        "description": "Expert mortgage brokering services for first-time homebuyers, helping Kiwis get on the property ladder with ease.",
        "nationwide": True,
        "tags": ["First Home Buyer", "Bad Credit History", "New to NZ"],
        "services": ["Home Loans", "KiwiSaver First Home Withdrawals", "Welcome Home Loan Scheme", "Debt Consolidation"],
        "endorsements": [
            {
                "name": "Sarah Thompson",
                "date": "May 9, 2024",
                "comment": "Kiwi Home Loans made my first home buying experience a breeze. Their knowledge of first home buyer schemes was invaluable.",
                "title": "Marketing Manager at Wellington Tech",
                "picture": "sarah_thompson.jpg"
            },
            {
                "name": "John Smith",
                "date": "June 4, 2024",
                "comment": "Great service and very professional.",
                "title": "Engineer at Auckland Engineering",
                "picture": "john_smith.jpg"
            }
        ]
    },
    {
        "id": 2,
        "name": "NZ Property Finance",
        "type": "Investment Property Specialist",
        "description": "A long-term partner for property investors looking to expand their portfolio across New Zealand...",
        "nationwide": True,
        "tags": ["Property Investor", "Commercial Property", "High Net Worth Individual"],
        "services": ["Investment Property Loans", "Commercial Property Finance", "Refinancing", "Construction Loans"],
        "endorsements": [
            {
                "name": "Michael Chen",
                "date": "Jun 17, 2024",
                "comment": "NZ Property Finance has been crucial in growing my property portfolio. Their market insights and negotiation skills with lenders are top-notch.",
                "title": "Director at Auckland Property Developments",
                "picture": "michael_chen.jpg"
            },
            {
                "name": "Jane Doe",
                "date": "July 1, 2024",
                "comment": "Very knowledgeable and helpful.",
                "title": "Investor at Wellington Investments",
                "picture": "jane_doe.jpg"
            }
        ]
    },
    {
        "id": 3,
        "name": "Fern Financials",
        "type": "Self-Employed Mortgage Specialist",
        "description": "Fern Financials is the go-to mortgage broker for self-employed Kiwis and small business owners seeking home loans...",
        "nationwide": True,
        "tags": ["Self-Employed", "Bad Credit History", "Refinancing"],
        "services": ["Home Loans", "Refinancing", "Debt Consolidation", "Construction Loans"],
        "endorsements": [
            {
                "name": "Emma Wilson",
                "date": "May 2, 2024",
                "comment": "As a freelancer, I thought getting a mortgage would be impossible. Fern Financials not only made it possible but made the whole process smooth and stress-free.",
                "title": "Freelance Graphic Designer",
                "picture": "emma_wilson.jpg"
            },
            {
                "name": "David Brown",
                "date": "June 20, 2024",
                "comment": "Excellent service and support.",
                "title": "Small Business Owner",
                "picture": "david_brown.jpg"
            }
        ]
    },
    {
        "id": 4,
        "name": "Koru Mortgages",
        "type": "Full-Service Mortgage Brokerage",
        "description": "We provide comprehensive mortgage solutions for all types of borrowers across New Zealand, from first-time buyers to seasoned investors.",
        "nationwide": True,
        "tags": ["First Home Buyer", "Property Investor", "Refinancing", "New to NZ", "Commercial Property"],
        "services": ["Home Loans", "Investment Property Loans", "Refinancing", "Commercial Property Finance", "KiwiSaver First Home Withdrawals"],
        "endorsements": [
            {
                "name": "James Tait",
                "date": "Apr 10, 2024",
                "comment": "Koru Mortgages has been my go-to for all things property finance. Their expertise across different loan types and lenders is unmatched.",
                "title": "CEO of Christchurch Retail Group",
                "picture": "james_tait.jpg"
            },
            {
                "name": "Laura White",
                "date": "July 15, 2024",
                "comment": "Very efficient and reliable.",
                "title": "Real Estate Agent",
                "picture": "laura_white.jpg"
            }
        ]
    }
]

@app.route('/')
def home():
    return render_template('home.html', cpas=cpas, title="Find the best mortgage brokers in NZ")

@app.route('/cpa/<int:cpa_id>')
def cpa_detail(cpa_id):
    cpa = next((cpa for cpa in cpas if cpa['id'] == cpa_id), None)
    if cpa:
        return render_template('cpa_detail.html', cpa=cpa)
    else:
        abort(404)

@app.route('/specialty/<type>')
def specialty(type):
    filtered_cpas = [cpa for cpa in cpas if type in [tag.replace(' ', '-').lower() for tag in cpa['tags']]]
    return render_template('home.html', cpas=filtered_cpas, title=f"Top {type.replace('-', ' ').title()} Expert Firms")

@app.route('/service/<type>')
def service(type):
    filtered_cpas = [cpa for cpa in cpas if type in [service.replace(' ', '-').lower() for service in cpa['services']]]
    return render_template('home.html', cpas=filtered_cpas, title=f"{type.replace('-', ' ').title()}")

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    cpa_id = int(data.get('cpa_id'))
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    profession = data.get('profession')
    household_income = data.get('household_income')

    # Find the CPA by ID
    cpa = next((cpa for cpa in cpas if cpa['id'] == cpa_id), None)
    if not cpa:
        return jsonify({'success': False, 'message': 'CPA not found'}), 404

    # Construct the email message
    subject = f"New request for {cpa['name']}"
    body = f"""
    You have a new contact request from {first_name} {last_name}.

    Email: {email}
    Profession: {profession}
    Household Tax Income: {household_income}
    
    Please forward this message to the appropriate person at {cpa['name']} for follow-up.
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