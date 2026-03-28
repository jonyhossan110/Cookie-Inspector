
        function tjmShouldShowModal() {
            const lastShown = localStorage.getItem("tjmModalLastShown");
            if (!lastShown) return true;
            
            const now = new Date().getTime();
            const cookieHours = typeof tjm_vars !== "undefined" ? tjm_vars.cookie_hours * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
            return (now - lastShown) > cookieHours;
        }

        function tjmSetModalShown() {
            localStorage.setItem("tjmModalLastShown", new Date().getTime());
        }

        function tjmShowModalWithDelay() {
            if (tjmShouldShowModal()) {
                setTimeout(function() {
                    document.getElementById("tjmTelegramModal").classList.add("show");
                    tjmSetModalShown();
                    
                    // Auto close after 1 minute (60000 milliseconds)
                    setTimeout(function() {
                        tjmCloseModal();
                    }, 60000);
                }, typeof tjm_vars !== "undefined" ? tjm_vars.delay_seconds : 5000);
            }
        }

        function tjmCloseModal() {
            document.getElementById("tjmTelegramModal").classList.remove("show");
        }

        function tjmJoinTelegram() {
            window.location.href = typeof tjm_vars !== "undefined" ? tjm_vars.telegram_link : "https://t.me/your_telegram_group";
        }

        // Check and show modal on page load
        window.onload = tjmShowModalWithDelay;
        