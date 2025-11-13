 function toggleSidebar() {
      const sidebar = document.getElementById('sidebar');
      const overlay = document.getElementById('overlay');
      const hamburger = document.getElementById('hamburger');
      
      sidebar.classList.toggle('active');
      overlay.classList.toggle('active');
      hamburger.classList.toggle('active');
    }

    // Set active menu item on click
    document.querySelectorAll('#sidebar ul li a').forEach(item => {
      item.addEventListener('click', function() {
        document.querySelectorAll('#sidebar ul li a').forEach(link => {
          link.classList.remove('active');
        });
        this.classList.add('active');
        
        // Close sidebar on mobile after selection
        if (window.innerWidth <= 768) {
          toggleSidebar();
        }
      });
    });

    // Add dynamic notification badges
    function updateBadges() {
      const badges = document.querySelectorAll('.menu-badge');
      badges.forEach(badge => {
        // Simulate changing badge counts
        const current = parseInt(badge.textContent);
        const change = Math.random() > 0.7 ? 1 : 0;
        if (change && current < 20) {
          badge.textContent = current + 1;
          badge.style.animation = 'pulse 0.5s';
          setTimeout(() => {
            badge.style.animation = '';
          }, 500);
        }
      });
    }

    // Update badges every 10 seconds
    setInterval(updateBadges, 10000);

    // Add pulse animation for badges
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
      }
    `;
    document.head.appendChild(style);

    // Dynamic user status indicator
    function updateUserStatus() {
      const status = document.querySelector('.user-status');
      if (status) {
        // Simulate status changes
        const isOnline = Math.random() > 0.2;
        status.style.backgroundColor = isOnline ? '#2ecc71' : '#e74c3c';
      }
    }

    // Update user status every 30 seconds
    setInterval(updateUserStatus, 30000);