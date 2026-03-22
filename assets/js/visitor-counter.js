// Visitor Counter Module
const visitorCounter = {
  API_BASE: 'http://localhost:8000', // Local backend

  // Initialize visitor counter on page load
  init: async function() {
    try {
      // Increment visitor count
      const response = await fetch(`${this.API_BASE}/api/visitors/increment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          this.displayCount(data.count);
        }
      } else {
        // Fallback if API fails
        this.displayCountOffline();
      }
    } catch (error) {
      console.error('Error incrementing visitor count:', error);
      this.displayCountOffline();
    }
  },

  // Display visitor count on page
  displayCount: function(count) {
    const visitorElements = document.querySelectorAll('.visitor_number');
    visitorElements.forEach(element => {
      element.textContent = `Visitor No.- ${this.formatNumber(count)}`;
    });
  },

  // Fallback display when offline
  displayCountOffline: function() {
    const visitorElements = document.querySelectorAll('.visitor_number');
    visitorElements.forEach(element => {
      if (!element.textContent || element.textContent.includes('0')) {
        element.textContent = 'Visitor No.- [Loading...]';
      }
    });
  },

  // Format number with commas
  formatNumber: function(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  },

  // Get current count without incrementing
  getCount: async function() {
    try {
      const response = await fetch(`${this.API_BASE}/api/visitors/count`);
      if (response.ok) {
        const data = await response.json();
        return data.success ? data.count : 0;
      }
      return 0;
    } catch (error) {
      console.error('Error fetching visitor count:', error);
      return 0;
    }
  }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => visitorCounter.init());
} else {
  visitorCounter.init();
}
