const MapaRegionalGeometry = (function () {
    "use strict";

    function projectedFeatureCentroid(feature, path, projection, d3) {
        const pathCentroid = path.centroid(feature);
        if (
            Array.isArray(pathCentroid) &&
            Number.isFinite(pathCentroid[0]) &&
            Number.isFinite(pathCentroid[1])
        ) {
            return pathCentroid;
        }

        const geographicCentroid = d3.geoCentroid(feature);
        const projectedCentroid = projection(geographicCentroid);
        if (
            Array.isArray(projectedCentroid) &&
            Number.isFinite(projectedCentroid[0]) &&
            Number.isFinite(projectedCentroid[1])
        ) {
            return projectedCentroid;
        }

        return null;
    }

    function separatedMicroterritoryPositions(
        features,
        path,
        projection,
        d3,
        minimumSeparation
    ) {
        const positioned = features.map(function (feature) {
            return {
                feature: feature,
                position: projectedFeatureCentroid(feature, path, projection, d3)
            };
        });
        if (positioned.some(function (item) { return item.position === null; })) {
            throw new Error("Microterritory geometry has no valid projected centroid.");
        }
        if (positioned.length === 2) {
            const deltaX = positioned[1].position[0] - positioned[0].position[0];
            const deltaY = positioned[1].position[1] - positioned[0].position[1];
            const distance = Math.hypot(deltaX, deltaY);
            if (distance < minimumSeparation) {
                const directionX = distance > 0 ? deltaX / distance : 1;
                const directionY = distance > 0 ? deltaY / distance : 0;
                const displacement = (minimumSeparation - distance) / 2;
                positioned[0].position = [
                    positioned[0].position[0] - directionX * displacement,
                    positioned[0].position[1] - directionY * displacement
                ];
                positioned[1].position = [
                    positioned[1].position[0] + directionX * displacement,
                    positioned[1].position[1] + directionY * displacement
                ];
            }
        }
        return positioned;
    }

    return {
        projectedFeatureCentroid: projectedFeatureCentroid,
        separatedMicroterritoryPositions: separatedMicroterritoryPositions
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
    const microterritoryGeoIds = new Set(["531", "533"]);
    const microterritoryMinimumSeparation = 34;
    const selectedIds = new Set();
    const coordinatedHighlightedIds = new Set();
    let memberPaths = null;
    let interactiveCountryPaths = null;
    let microterritoryControls = null;

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

        if (microterritoryControls) {
            microterritoryControls
                .classed("is-selected", function (feature) {
                    const country = countryForFeature(feature);
                    return country && selectedIds.has(String(country.id));
                })
                .classed("is-coordinated", function (feature) {
                    const country = countryForFeature(feature);
                    return country && coordinatedHighlightedIds.has(String(country.id));
                })
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
            .on("click", function (event, feature) {
                toggleCountry(countryForFeature(feature));
            })
            .on("keydown", function (event, feature) {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    toggleCountry(countryForFeature(feature));
                }
            })
            .on("pointermove", function (event, feature) {
                showTooltip(event, countryForFeature(feature));
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
            });

        memberPaths
            .filter(function (feature) {
                return microterritoryGeoIds.has(
                    String(feature.id).padStart(3, "0")
                );
            })
            .classed("is-microterritory", true)
            .attr("aria-hidden", "true")
            .attr("focusable", "false");

        interactiveCountryPaths = bindCountryControl(
            memberPaths.filter(function (feature) {
                return !microterritoryGeoIds.has(
                    String(feature.id).padStart(3, "0")
                );
            })
        );

        const microterritoryFeatures = features.filter(function (feature) {
            const geoId = String(feature.id).padStart(3, "0");
            return microterritoryGeoIds.has(geoId) && countriesByGeoId.has(geoId);
        });
        const institutionalMicroterritoryGeoIds = new Set(
            Array.from(microterritoryGeoIds).filter(function (geoId) {
                return countriesByGeoId.has(geoId);
            })
        );
        if (microterritoryFeatures.length !== institutionalMicroterritoryGeoIds.size) {
            throw new Error("Institutional microterritory geometry is unavailable.");
        }
        const positionedMicroterritories = MapaRegionalGeometry.separatedMicroterritoryPositions(
            microterritoryFeatures,
            path,
            projection,
            window.d3,
            microterritoryMinimumSeparation
        );
        microterritoryControls = svg
            .append("g")
            .attr("class", "home-map-microterritory-layer")
            .selectAll("g")
            .data(positionedMicroterritories)
            .join("g")
            .attr("class", "home-map-microterritory-control")
            .attr("transform", function (item) {
                return "translate(" + item.position[0] + "," + item.position[1] + ")";
            });

        microterritoryControls
            .append("circle")
            .attr("class", "home-map-microterritory-hit")
            .attr("r", 16);
        microterritoryControls
            .append("circle")
            .attr("class", "home-map-microterritory-marker")
            .attr("r", 8);
        microterritoryControls
            .append("title")
            .text(function (item) {
                return countryForFeature(item.feature).nome;
            });
        bindCountryControl(
            microterritoryControls.datum(function (item) { return item.feature; })
        );

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
