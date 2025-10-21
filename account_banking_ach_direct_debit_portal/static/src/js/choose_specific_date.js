document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const startDate = document.getElementById("start-date");
    const repeatDay = document.getElementById("repeat-day");

    function ordinal(n) {
        const j = n % 10,
            k = n % 100;
        if (j === 1 && k !== 11) return n + "st";
        if (j === 2 && k !== 12) return n + "nd";
        if (j === 3 && k !== 13) return n + "rd";
        return n + "th";
    }

    if (startDate) {
        startDate.addEventListener("change", function () {
            const val = this.value;

            fetch("/autopay-specific-date/change", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": odoo.csrf_token,
                },
                body: JSON.stringify({specific_date: val}),
            })
                .then((r) => r.json())
                .then((data) => {
                    if (data.status === "success" && repeatDay && data.day) {
                        repeatDay.textContent = ordinal(data.day);
                    } else {
                        console.warn("Update failed:", data.error || data);
                    }
                })
                .catch((err) => console.error("Error updating date:", err));
        });

        const day = new Date(startDate.value).getDate();
        if (day) {
            repeatDay.textContent = ordinal(day);
        }
    }
});
