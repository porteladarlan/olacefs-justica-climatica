(function () {
    "use strict";

    const navigation = document.querySelector(".climate-examples-nav");
    if (!navigation) {
        return;
    }

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    navigation.addEventListener("click", function (event) {
        const link = event.target.closest(".climate-examples-nav-card");
        if (!link) {
            return;
        }

        const targetId = link.getAttribute("href");
        const target = targetId ? document.querySelector(targetId) : null;
        if (!target) {
            return;
        }

        event.preventDefault();
        window.history.pushState(null, "", targetId);
        target.focus({ preventScroll: true });
        target.scrollIntoView({
            behavior: reduceMotion.matches ? "auto" : "smooth",
            block: "start",
        });
    });
}());
