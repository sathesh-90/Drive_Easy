document.addEventListener("DOMContentLoaded", function() {
  // Calculate pending amounts dynamically including damage
  document.querySelectorAll('.booking-card').forEach(card => {
    const totalElem = card.querySelector('.total-amount');
    const advanceElem = card.querySelector('.advance-payment');
    const damageElem = card.querySelector('.damage-fee');
    const pendingElem = card.querySelector('.pending-payment');
    const totalWithDamageElem = card.querySelector('.total-with-damage');

    let total = parseFloat(totalElem.textContent) || 0;
    let advance = parseFloat(advanceElem.textContent) || 0;
    let damage = parseFloat(damageElem?.textContent || 0);

    let totalWithDamage = total + damage;
    let pending = Math.max(totalWithDamage - advance, 0);

    if (totalWithDamageElem) {
      totalWithDamageElem.textContent = totalWithDamage.toFixed(2);
    }
    if (pendingElem) {
      pendingElem.textContent = pending.toFixed(2);
    }
  });

  // Add smooth animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe booking cards for animation
  document.querySelectorAll('.booking-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
  });
});