document.addEventListener('DOMContentLoaded', function() {
  var modal = document.getElementById('contactModal');
  var btn = document.querySelector('.actions .contact-btn');
  var span = document.getElementsByClassName('close')[0];
  var form = document.getElementById('contactForm');

  btn.onclick = function() {
    modal.style.display = 'block';
  }

  span.onclick = function() {
    modal.style.display = 'none';
  }

  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  }

  form.onsubmit = function(e) {
    e.preventDefault();
    var email = document.getElementById('email').value;
    var message = document.getElementById('message').value;
    var cpaId = document.getElementById('cpa_id').value;

    fetch('/send_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cpa_id: cpaId,
        email: email,
        message: message
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
});