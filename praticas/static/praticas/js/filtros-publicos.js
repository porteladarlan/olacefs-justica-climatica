(function () {
    "use strict";

    const groups = Array.from(
        document.querySelectorAll("[data-filter-disclosure]")
    );

    function closeGroup(group) {
        const search = group.querySelector("[data-filter-search]");
        const panel = group.querySelector(".catalog-filter-panel");
        if (panel) {
            panel.classList.remove("is-open");
        }
        if (search) {
            search.setAttribute("aria-expanded", "false");
        }
    }

    function openGroup(group) {
        groups.forEach(function (otherGroup) {
            if (otherGroup !== group) {
                closeGroup(otherGroup);
            }
        });
        const search = group.querySelector("[data-filter-search]");
        const panel = group.querySelector(".catalog-filter-panel");
        if (panel) {
            panel.classList.add("is-open");
        }
        if (search) {
            search.setAttribute("aria-expanded", "true");
        }
    }

    groups.forEach(function (group) {
        const search = group.querySelector("[data-filter-search]");
        const options = Array.from(
            group.querySelectorAll("[data-filter-option]")
        );
        const empty = group.querySelector("[data-filter-empty]");

        if (search) {
            search.addEventListener("focus", function () {
                openGroup(group);
            });
            search.addEventListener("click", function () {
                openGroup(group);
            });
            search.addEventListener("input", function () {
                const term = search.value.trim().toLocaleLowerCase();
                let visible = 0;
                options.forEach(function (option) {
                    const matches = option.textContent
                        .toLocaleLowerCase()
                        .includes(term);
                    option.hidden = !matches;
                    if (matches) {
                        visible += 1;
                    }
                });
                if (empty) {
                    empty.hidden = visible !== 0;
                }
                openGroup(group);
            });
            search.addEventListener("keydown", function (event) {
                if (event.key === "Escape") {
                    closeGroup(group);
                    search.focus();
                } else if (event.key === "Enter") {
                    event.preventDefault();
                }
            });
        }

        group.querySelectorAll('input[type="checkbox"]').forEach(function (input) {
            input.addEventListener("change", function () {
                const form = input.form;
                if (form && typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                } else if (form) {
                    form.submit();
                }
            });
        });
    });

    document.addEventListener("click", function (event) {
        groups.forEach(function (group) {
            if (!group.contains(event.target)) {
                closeGroup(group);
            }
        });
    });

    document.querySelectorAll("[data-auto-submit]").forEach(function (control) {
        control.addEventListener("change", function () {
            const form = control.form;
            if (form && typeof form.requestSubmit === "function") {
                form.requestSubmit();
            } else if (form) {
                form.submit();
            }
        });
    });

    document.querySelectorAll("[data-add-filter]").forEach(function (control) {
        control.addEventListener("change", function () {
            if (!control.value) {
                return;
            }
            const params = new URLSearchParams(window.location.search);
            params.append(control.dataset.addFilter, control.value);
            window.location.assign(window.location.pathname + "?" + params.toString());
        });
    });
})();
