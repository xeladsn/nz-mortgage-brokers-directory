from flask import Flask, render_template, abort

app = Flask(__name__)

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
                "title": "Marketing Manager at Wellington Tech"
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
                "title": "Director at Auckland Property Developments"
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
                "title": "Freelance Graphic Designer"
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
                "title": "CEO of Christchurch Retail Group"
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

if __name__ == '__main__':
    app.run(debug=True)