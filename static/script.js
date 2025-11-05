// Navigation Section Switching
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        link.classList.add('active');
        
        // Get section name from data attribute
        const sectionName = link.getAttribute('data-section');
        
        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            mynotes: 'Catatan Pribadi',
            myfiles: 'File Pribadi',
            mypictures: 'Galeri Pribadi'
        };
        
        document.querySelector('.page-title').textContent = titles[sectionName] || 'Dashboard';
        
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show selected section
        document.getElementById(`${sectionName}-section`).classList.add('active');
        
        // Close sidebar on mobile
        const sidebar = document.querySelector('.sidebar');
        if (sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
        }
    });
});

// Toggle Sidebar on Mobile
document.getElementById('toggleSidebar').addEventListener('click', () => {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
});

// Close sidebar when clicking outside
document.addEventListener('click', (e) => {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');
    
    if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('active');
    }
});

// Close sidebar when window is resized above 768px
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        document.querySelector('.sidebar').classList.remove('active');
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Set first nav item as active
    document.querySelector('.nav-link').classList.add('active');
    document.getElementById('dashboard-section').classList.add('active');
});