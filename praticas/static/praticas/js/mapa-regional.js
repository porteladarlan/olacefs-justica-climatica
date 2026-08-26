const MapaRegionalGeometry = (function () {
    "use strict";

    function pastelPaletteIndex(geoId) {
        const normalizedId = String(geoId || "")
            .split("")
            .reduce(function (total, digit) {
                return total + (Number(digit) || 0);
            }, 0);
        return normalizedId % 4;
    }

    return {
        pastelPaletteIndex: pastelPaletteIndex
    };
})();

if (typeof module !== "undefined" && module.exports) {
    module.exports = MapaRegionalGeometry;
}

(function () {
    "use strict";

    if (typeof document === "undefined") {
        return;
    }

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
    const coordinatedSelect = document.getElementById("regionalMapCoordinatedAudit");
    const coordinatedStatus = document.getElementById("regionalMapCoordinatedStatus");
    const coordinatedInitialStatus = coordinatedStatus
        ? coordinatedStatus.textContent.trim()
        : "";
    const actionButtons = Array.from(form.querySelectorAll("button[type='submit']"));
    const countryRadios = Array.from(
        form.querySelectorAll("input[type='radio'][name='pais']")
    );

    let payload;
    try {
        payload = JSON.parse(dataElement.textContent);
    } catch (error) {
        showLoadError();
        return;
    }

    const countries = Array.isArray(payload.paises) ? payload.paises : [];
    const coordinatedAudits = Array.isArray(payload.auditorias_coordenadas)
        ? payload.auditorias_coordenadas
        : [];
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
    const coordinatedAuditsById = new Map(
        coordinatedAudits.map(function (audit) {
            return [String(audit.id), audit];
        })
    );
    const selectedIds = new Set();
    const coordinatedHighlightedIds = new Set();
    let memberPaths = null;
    let interactiveCountryPaths = null;

    function selectedCountries() {
        return countries.filter(function (country) {
            return selectedIds.has(String(country.id));
        });
    }

    function accessibleCountryLabel(country, isSelected, isCoordinated) {
        const state = isSelected
            ? section.dataset.selectedLabel
            : section.dataset.unselectedLabel;
        let label = section.dataset.countryLabel + " " + country.nome + ", " + state;
        if (isCoordinated) {
            label += ", " + section.dataset.coordinatedLabel;
        }
        return label;
    }

    function countryForFeature(feature) {
        return countriesByGeoId.get(String(feature.id).padStart(3, "0"));
    }

    function updatePathState() {
        if (!memberPaths) {
            return;
        }
        memberPaths
            .classed("is-selected", function (feature) {
                const country = countryForFeature(feature);
                return country && selectedIds.has(String(country.id));
            })
            .classed("is-coordinated", function (feature) {
                const country = countryForFeature(feature);
                return country && coordinatedHighlightedIds.has(String(country.id));
            });

        if (interactiveCountryPaths) {
            interactiveCountryPaths
                .attr("aria-pressed", function (feature) {
                    const country = countryForFeature(feature);
                    return country && selectedIds.has(String(country.id))
                        ? "true"
                        : "false";
                })
                .attr("aria-label", function (feature) {
                    const country = countryForFeature(feature);
                    return accessibleCountryLabel(
                        country,
                        selectedIds.has(String(country.id)),
                        coordinatedHighlightedIds.has(String(country.id))
                    );
                });
        }

    }

    function updateCount(total) {
        if (total === 0) {
            count.textContent = section.dataset.selectedZero;
        } else {
            count.textContent = section.dataset.selectedOne;
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

        countryRadios.forEach(function (radio) {
            radio.checked = selectedIds.has(radio.value);
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
        hideTooltip();
        if (selected) {
            selectedIds.clear();
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

    function updateCoordinatedHighlight(auditId) {
        coordinatedHighlightedIds.clear();
        const audit = coordinatedAuditsById.get(String(auditId));

        if (audit) {
            (audit.paises || []).forEach(function (country) {
                coordinatedHighlightedIds.add(String(country.id));
            });
            if (coordinatedStatus) {
                const countryNames = (audit.paises || []).map(function (country) {
                    return country.nome;
                });
                coordinatedStatus.textContent = section.dataset.coordinatedSummary
                    .replace("{audit}", audit.titulo)
                    .replace("{countries}", countryNames.join(", "));
            }
        } else if (coordinatedStatus) {
            coordinatedStatus.textContent = coordinatedInitialStatus;
        }

        updatePathState();
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

    function bindCountryControl(selection) {
        let pointerDownPoint = null;
        return selection
            .attr("role", "button")
            .attr("tabindex", "0")
            .attr("data-country-id", function (feature) {
                return String(countryForFeature(feature).id);
            })
            .attr("aria-pressed", "false")
            .attr("aria-label", function (feature) {
                return accessibleCountryLabel(countryForFeature(feature), false, false);
            })
            .on("pointerdown", function (event) {
                pointerDownPoint = [event.clientX, event.clientY];
            })
            .on("click", function (event, feature) {
                if (pointerDownPoint) {
                    const distance = Math.hypot(
                        event.clientX - pointerDownPoint[0],
                        event.clientY - pointerDownPoint[1]
                    );
                    pointerDownPoint = null;
                    if (distance > 5 || event.defaultPrevented) {
                        hideTooltip();
                        return;
                    }
                }
                hideTooltip();
                toggleCountry(countryForFeature(feature));
            })
            .on("keydown", function (event, feature) {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    toggleCountry(countryForFeature(feature));
                }
            })
            .on("pointermove", function (event, feature) {
                const country = countryForFeature(feature);
                if (country && selectedIds.has(String(country.id))) {
                    hideTooltip();
                    return;
                }
                showTooltip(event, country);
            })
            .on("pointerleave", hideTooltip)
            .on("blur", hideTooltip);
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
        const width = 620;
        const height = 600;
        const collection = {type: "FeatureCollection", features: features};
        const projection = window.d3
            .geoMercator()
            .fitExtent([[12, 12], [width - 12, height - 12]], collection);
        const path = window.d3.geoPath(projection);
        const svg = window.d3
            .select(mapContainer)
            .append("svg")
            .attr("viewBox", "0 0 " + width + " " + height)
            .attr("role", "group")
            .attr("aria-label", document.getElementById("home-map-title").textContent.trim());
        svg.append("title").text(document.getElementById("home-map-title").textContent.trim());

        const zoomLayer = svg.append("g").attr("class", "home-map-zoom-layer");
        const zoomBehavior = window.d3.zoom()
            .scaleExtent([1, 8])
            .on("zoom", function (event) {
                zoomLayer.attr("transform", event.transform);
            });
        svg.call(zoomBehavior);
        svg.on("click.zoom-selection", function (event) {
            if (event.defaultPrevented) {
                event.stopImmediatePropagation();
            }
        });

        const zoomIn = document.getElementById("regionalMapZoomIn");
        const zoomOut = document.getElementById("regionalMapZoomOut");
        const zoomReset = document.getElementById("regionalMapZoomReset");
        if (zoomIn) {
            zoomIn.addEventListener("click", function () {
                svg.transition().duration(180).call(zoomBehavior.scaleBy, 1.6);
            });
        }
        if (zoomOut) {
            zoomOut.addEventListener("click", function () {
                svg.transition().duration(180).call(zoomBehavior.scaleBy, 0.625);
            });
        }
        if (zoomReset) {
            zoomReset.addEventListener("click", function () {
                svg.transition().duration(180).call(zoomBehavior.transform, window.d3.zoomIdentity);
            });
        }

        const paths = zoomLayer
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
            .attr("data-palette-index", function (feature) {
                return MapaRegionalGeometry.pastelPaletteIndex(
                    String(feature.id).padStart(3, "0")
                );
            });

        interactiveCountryPaths = bindCountryControl(memberPaths);

        updatePathState();
    }

    countryRadios.forEach(function (radio) {
        radio.addEventListener("change", function () {
            if (radio.checked) {
                setCountrySelected(radio.value, true);
            }
        });
    });

    if (coordinatedSelect) {
        coordinatedSelect.addEventListener("change", function () {
            updateCoordinatedHighlight(coordinatedSelect.value);
        });
    }

    chips.addEventListener("click", function (event) {
        const button = event.target.closest("button[data-country-id]");
        if (button) {
            const countryId = button.dataset.countryId;
            setCountrySelected(countryId, false);
            const mapControl = mapContainer.querySelector(
                "[data-country-id='" + countryId + "']"
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
