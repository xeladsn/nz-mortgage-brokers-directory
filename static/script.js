document.addEventListener('DOMContentLoaded', function() {
  var modal = document.getElementById('contactModal');
  var btn = document.querySelector('.actions .contact-btn');
  var span = document.getElementsByClassName('close')[0];
  var form = document.getElementById('contactForm');

  if (btn) {
    btn.onclick = function() {
      modal.style.display = 'block';
    }
  }

  if (span) {
    span.onclick = function() {
      modal.style.display = 'none';
    }
  }

  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  }

  if (form) {
    form.onsubmit = function(e) {
      e.preventDefault();
      var name = document.getElementById('name').value;
      var email = document.getElementById('email').value;
      var phone = document.getElementById('phone').value;
      var loanPurpose = document.getElementById('loan_purpose').value;
      var householdIncome = document.getElementById('household_income').value;
      var purchaseLocation = document.getElementById('purchase_location').value;
      var depositAmount = document.getElementById('deposit_amount').value;
      var additionalInfo = document.getElementById('additional_info').value;
      var maId = document.getElementById('ma_id').value;

      // Get selected deposit sources
      var depositSources = [];
      document.querySelectorAll('input[name="deposit_source"]:checked').forEach(function(checkbox) {
        depositSources.push(checkbox.value);
      });

      // Validate required fields
      var requiredFields = {
        'name': name,
        'email': email,
        'phone': phone
      };

      var missingFields = [];
      for (var field in requiredFields) {
        if (!requiredFields[field]) {
          missingFields.push(field);
        }
      }

      if (missingFields.length > 0) {
        alert('Please fill in the following required fields: ' + missingFields.join(', '));
        return;
      }

      fetch('/send_message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ma_id: maId,
          name: name,
          email: email,
          phone: phone,
          loan_purpose: loanPurpose,
          household_income: householdIncome,
          purchase_location: purchaseLocation,
          deposit_amount: depositAmount,
          deposit_sources: depositSources,
          additional_info: additionalInfo
        }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('Message sent successfully!');
          form.reset();
          modal.style.display = 'none';
        } else {
          alert('Failed to send message. Please try again.');
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
      });
    }
  }
});