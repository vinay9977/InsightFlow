// Sidebar toggle functionality for mobile view
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const sidebarTexts = document.querySelectorAll('.sidebar-text');
    
    if (sidebarToggle && sidebar) {
        // On mobile, handle toggle button click
        sidebarToggle.addEventListener('click', function() {
            // Toggle sidebar visibility
            sidebar.classList.toggle('translate-x-0');
            sidebar.classList.toggle('-translate-x-full');
            
            // Add expanded class on mobile for full width
            sidebar.classList.toggle('mobile-expanded');
            if (sidebar.classList.contains('mobile-expanded')) {
                sidebar.style.width = '14rem';
                // Show text and adjust alignment
                sidebarLinks.forEach(link => link.style.justifyContent = 'flex-start');
                sidebarTexts.forEach(text => {
                    text.style.display = 'inline';
                    text.style.opacity = '1';
                });
            } else {
                sidebar.style.width = '4rem';
                // Hide text and center icons
                sidebarLinks.forEach(link => link.style.justifyContent = 'center');
                sidebarTexts.forEach(text => {
                    text.style.display = 'none';
                    text.style.opacity = '0';
                });
            }
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isMobile = window.innerWidth < 768; // md breakpoint
            const isClickOutsideSidebar = !sidebar.contains(event.target);
            const isClickSidebarToggle = sidebarToggle.contains(event.target);
            
            if (isMobile && isClickOutsideSidebar && !isClickSidebarToggle && sidebar.classList.contains('translate-x-0')) {
                sidebar.classList.remove('translate-x-0');
                sidebar.classList.add('-translate-x-full');
                sidebar.classList.remove('mobile-expanded');
                sidebar.style.width = '4rem';
                // Reset to centered icons
                sidebarLinks.forEach(link => link.style.justifyContent = 'center');
                sidebarTexts.forEach(text => {
                    text.style.display = 'none';
                    text.style.opacity = '0';
                });
            }
        });
        
        // Reset sidebar width on resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768) {
                // On desktop, reset to default state (not explicitly expanded)
                sidebar.classList.remove('mobile-expanded');
                sidebar.style.width = ''; // Let CSS handle it
                sidebarLinks.forEach(link => link.style.justifyContent = '');
                sidebarTexts.forEach(text => {
                    text.style.display = '';
                    text.style.opacity = '';
                });
            } else if (!sidebar.classList.contains('translate-x-0')) {
                // For mobile when sidebar is closed
                sidebar.style.width = '4rem';
                sidebarLinks.forEach(link => link.style.justifyContent = 'center');
                sidebarTexts.forEach(text => {
                    text.style.display = 'none';
                    text.style.opacity = '0';
                });
            }
        });
    }
}); 