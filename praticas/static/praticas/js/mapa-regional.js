(function () {
    "use strict";

    const section = document.getElementById("mapSection");
    const dataElement = document.getElementById("regional-map-data");
    if (!section || !dataElement) {
        return;
    }

    const mapContainer = document.getElementById("regionalMap");
    const tooltip = document.getElementById("regionalMapTooltip");
    const form = document.getElementById("regionalMapForm");
    const emptyState = document.getElementById("regionalMapEmpty");
    const selectionState = document.getElementById("regionalMapSelection");
    const count = document.getElementById("regionalMapCount");
    const chips = document.getElementById("regionalMapChips");
    const efsList = document.getElementById("regionalMapEfs");
    const experiences = document.getElementById("regionalMapExperiences");
    const norms = document.getElementById("regionalMapNorms");
    const clearButton = document.getElementById("regionalMapClear");
    const actionButtons = Array.from(form.querySelectorAll("button[type='submit']"));
    const countryCheckboxes = Array.from(form.querySelectorAll("input[name='pais']"));

    let payload;
    try {
        payload = JSON.parse(dataElement.textContent);
    } catch (error) {
        showLoadError();
        return;
    }

    const countries = Array.isArray(payload.paises) ? payload.paises : [];
    const countriesByGeoId = new Map(
        countries.map(function (country) {
            return [String(country.geo_id).padStart(3, "0"), country];
        })
    );
    const countriesById = new Map(
        countries.map(function (country) {
            return [String(country.id), country];
        })
    );
    const regionGeoIds = new Set(
        (payload.geo_ids_regiao || []).map(function (geoId) {
            return String(geoId).padStart(3, "0");
        })
    );
    const selectedIds = new Set();
    let memberPaths = null;

    function selectedCountries() {
        return countries.filter(function (country) {
            return selectedIds.has(String(country.id));
        });
    }

    function accessibleCountryLabel(country, isSelected) {
        const state = isSelected
            ? section.dataset.selectedLabel
            : section.dataset.unselectedLabel;
        return section.dataset.countryLabel + " " + country.nome + ", " + state;
    }

    function updatePathState() {
        if (!memberPaths) {
            return;
        }
        memberPaths
            .classed("is-selected", function (feature) {
                const country = countriesByGeoId.get(
                    String(feature.id).padStart(3, "0")
                );
                return country && selectedIds.has(String(country.id));
            })
            .attr("aria-pressed", function (feature) {
                const country = countriesByGeoId.get(
                    String(feature.id).padStart(3, "0")
                );
                return country && selectedIds.has(String(country.id)) ? "true" : "false";
            })
            .attr("aria-label", function (feature) {
                const country = countriesByGeoId.get(
                    String(feature.id).padStart(3, "0")
                );
                return accessibleCountryLabel(
                    country,
                    selectedIds.has(String(country.id))
                );
            });
    }

    function updateCount(total) {
        if (total === 0) {
            count.textContent = section.dataset.selectedZero;
        } else if (total === 1) {
            count.textContent = section.dataset.selectedOne;
        } else {
            count.textContent = section.dataset.selectedMany.replace("{count}", total);
        }
    }

    function renderSelection() {
        const selected = selectedCountries();
        const hasSelection = selected.length > 0;

        emptyState.hidden = hasSelection;
        selectionState.hidden = !hasSelection;
        actionButtons.forEach(function (button) {
            button.disabled = !hasSelection;
        });
        clearButton.disabled = !hasSelection;
        updateCount(selected.length);

        countryCheckboxes.forEach(function (checkbox) {
            checkbox.checked = selectedIds.has(checkbox.value);
        });

        chips.replaceChildren();
        efsList.replaceChildren();

        let totalExperiences = 0;
        const normativeIds = new Set();
        selected.forEach(function (country) {
            totalExperiences += Number(country.experiencias_publicadas) || 0;
            (country.criterios_normativos_ids || []).forEach(function (normId) {
                normativeIds.add(String(normId));
            });

            const chip = document.createElement("button");
            chip.type = "button";
            chip.className = "home-map-chip";
            chip.dataset.countryId = String(country.id);
            chip.setAttribute(
                "aria-label",
                section.dataset.removeLabel + " " + country.nome
            );
            chip.append(document.createTextNode(country.nome + " "));
            const close = document.createElement("span");
            close.setAttribute("aria-hidden", "true");
            close.textContent = "×";
            chip.append(close);
            chips.append(chip);

            (country.efs || []).forEach(function (efs) {
                const item = document.createElement("li");
                item.textContent = efs.sigla
                    ? efs.nome + " (" + efs.sigla + ")"
                    : efs.nome;
                efsList.append(item);
            });
        });

        experiences.textContent = String(totalExperiences);
        norms.textContent = String(normativeIds.size);
        updatePathState();
    }

    function setCountrySelected(countryId, selected) {
        const normalizedId = String(countryId);
        if (!countriesById.has(normalizedId)) {
            return;
        }
        if (selected) {
            selectedIds.add(normalizedId);
        } else {
            selectedIds.delete(normalizedId);
        }
        renderSelection();
    }

    function toggleCountry(country) {
        const countryId = String(country.id);
        setCountrySelected(countryId, !selectedIds.has(countryId));
    }

    function showTooltip(event, country) {
        if (!tooltip || !country) {
            return;
        }
        tooltip.textContent = country.nome;
        tooltip.hidden = false;
        const card = tooltip.parentElement;
        const bounds = card.getBoundingClientRect();
        const maxX = Math.max(8, bounds.width - tooltip.offsetWidth - 8);
        const maxY = Math.max(8, bounds.height - tooltip.offsetHeight - 8);
        const x = Math.min(maxX, Math.max(8, event.clientX - bounds.left + 12));
        const y = Math.min(maxY, Math.max(8, event.clientY - bounds.top + 12));
        tooltip.style.left = x + "px";
        tooltip.style.top = y + "px";
    }

    function hideTooltip() {
        if (tooltip) {
            tooltip.hidden = true;
        }
    }

    function showLoadError() {
        if (!mapContainer) {
            return;
        }
        mapContainer.replaceChildren();
        const message = document.createElement("p");
        message.className = "home-map-error";
        message.setAttribute("role", "alert");
        message.textContent = section.dataset.loadError;
        mapContainer.append(message);
    }

    function buildMap(topology) {
        const worldObject = topology && topology.objects && topology.objects.countries;
        if (!worldObject || typeof window.d3 === "undefined" || typeof window.topojson === "undefined") {
            throw new Error("Map dependencies are unavailable.");
        }

        const features = window.topojson
            .feature(topology, worldObject)
            .features.filter(function (feature) {
                return regionGeoIds.has(String(feature.id).padStart(3, "0"));
            });
        if (!features.length) {
            throw new Error("Regional geometries are unavailable.");
        }

        mapContainer.replaceChildren();
        const width = 720;
        const height = 520;
        const collection = {type: "FeatureCollection", features: features};
        const projection = window.d3
            .geoMercator()
            .fitExtent([[24, 18], [width - 24, height - 18]], collection);
        const path = window.d3.geoPath(projection);
        const svg = window.d3
            .select(mapContainer)
            .append("svg")
            .attr("viewBox", "0 0 " + width + " " + height)
            .attr("role", "group")
            .attr("aria-label", document.getElementById("home-map-title").textContent.trim());
        svg.append("title").text(document.getElementById("home-map-title").textContent.trim());

        const paths = svg
            .append("g")
            .selectAll("path")
            .data(features)
            .join("path")
            .attr("d", path)
            .attr("class", function (feature) {
                return countriesByGeoId.has(String(feature.id).padStart(3, "0"))
                    ? "home-map-country is-member"
                    : "home-map-country is-other";
            });

        paths
            .filter(function (feature) {
                return !countriesByGeoId.has(String(feature.id).padStart(3, "0"));
            })
            .attr("aria-hidden", "true")
            .attr("focusable", "false");

        memberPaths = paths
            .filter(function (feature) {
                return countriesByGeoId.has(String(feature.id).padStart(3, "0"));
            })
            .attr("role", "button")
            .attr("tabindex", "0")
            .attr("data-country-id", function (feature) {
                return String(
                    countriesByGeoId.get(String(feature.id).padStart(3, "0")).id
                );
            })
            .attr("aria-pressed", "false")
            .attr("aria-label", function (feature) {
                return accessibleCountryLabel(
                    countriesByGeoId.get(String(feature.id).padStart(3, "0")),
                    false
                );
            })
            .on("click", function (event, feature) {
                toggleCountry(
                    countriesByGeoId.get(String(feature.id).padStart(3, "0"))
                );
            })
            .on("keydown", function (event, feature) {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    toggleCountry(
                        countriesByGeoId.get(String(feature.id).padStart(3, "0"))
                    );
                }
            })
            .on("pointermove", function (event, feature) {
                showTooltip(
                    event,
                    countriesByGeoId.get(String(feature.id).padStart(3, "0"))
                );
            })
            .on("pointerleave", hideTooltip)
            .on("blur", hideTooltip);

        updatePathState();
    }

    countryCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            setCountrySelected(checkbox.value, checkbox.checked);
        });
    });

    chips.addEventListener("click", function (event) {
        const button = event.target.closest("button[data-country-id]");
        if (button) {
            const countryId = button.dataset.countryId;
            setCountrySelected(countryId, false);
            const mapControl = mapContainer.querySelector(
                ".home-map-country[data-country-id='" + countryId + "']"
            );
            if (mapControl) {
                mapControl.focus();
            }
        }
    });

    form.addEventListener("reset", function () {
        selectedIds.clear();
        renderSelection();
    });

    renderSelection();

    if (typeof window.d3 === "undefined" || typeof window.topojson === "undefined") {
        showLoadError();
        return;
    }

    window.fetch(section.dataset.geoUrl, {credentials: "same-origin"})
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Unable to load regional geography.");
            }
            return response.json();
        })
        .then(buildMap)
        .catch(showLoadError);
})();
