document.addEventListener('DOMContentLoaded', function() {
    // Find all countdown elements
    const countdownElements = document.querySelectorAll('.survey-countdown');
    
    countdownElements.forEach(function(element) {
        try {
            // Parse the target date from the data attribute
            const targetDateStr = element.dataset.targetDate;
            if (!targetDateStr) return;
            
            // Try multiple date parsing approaches
            let targetDate;
            try {
                // ISO format
                targetDate = new Date(targetDateStr);
            } catch (e) {
                // Fallback to manual parsing
                targetDate = new Date(targetDateStr.replace(/-/g, '/'));
            }
            
            if (isNaN(targetDate.getTime())) return;
            
            const surveyId = element.dataset.surveyId;
            const countdownType = element.dataset.countdownType;
            
            // Elements to update
            const daysElement = element.querySelector('.countdown-days');
            const hoursElement = element.querySelector('.countdown-hours');
            const minutesElement = element.querySelector('.countdown-minutes');
            const secondsElement = element.querySelector('.countdown-seconds');
            
            // Initial update
            updateCountdown();
            
            // Update the countdown every second
            const interval = setInterval(updateCountdown, 1000);
            
            function updateCountdown() {
                // Get current date and time
                const now = new Date().getTime();
                
                // Find the distance between now and the target date
                const distance = targetDate.getTime() - now;
                
                // Time calculations for days, hours, minutes and seconds
                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                // Update the elements if the countdown hasn't finished
                if (distance > 0) {
                    daysElement.textContent = days;
                    hoursElement.textContent = hours;
                    minutesElement.textContent = minutes;
                    secondsElement.textContent = seconds;
                } else {
                    // If the countdown is over
                    clearInterval(interval);
                    
                    if (countdownType === 'start') {
                        // Survey has started - reload page to show active status
                        window.location.reload();
                    } else if (countdownType === 'end') {
                        // Survey has ended - reload page to show expired status
                        window.location.reload();
                    }
                }
            }
        } catch (error) {
            // Silent error handling
        }
    });
});