(function () {
    "use strict";

    const container = document.querySelector("[data-audit-questions]");
    if (!container) {
        return;
    }

    const list = container.querySelector("[data-question-list]");
    const addButton = container.querySelector("[data-add-question]");
    const questionLabel = container.dataset.questionLabel;
    const removeLabel = container.dataset.removeLabel;

    function renumber() {
        const rows = Array.from(list.querySelectorAll("[data-question-row]"));
        rows.forEach(function (row, index) {
            const number = index + 1;
            const textarea = row.querySelector("textarea");
            const label = row.querySelector("label");
            const numberText = row.querySelector("[data-question-number]");
            const remove = row.querySelector("[data-remove-question]");
            textarea.id = "id_pergunta_auditoria_" + number;
            label.htmlFor = textarea.id;
            numberText.textContent = questionLabel + " " + number;
            remove.setAttribute("aria-label", removeLabel + " " + number);
            remove.hidden = rows.length === 1;
        });
    }

    function createQuestion() {
        const row = document.createElement("div");
        row.className = "audit-question-row";
        row.dataset.questionRow = "";
        const label = document.createElement("label");
        const number = document.createElement("span");
        number.dataset.questionNumber = "";
        label.append(number);
        const control = document.createElement("div");
        control.className = "audit-question-control";
        const textarea = document.createElement("textarea");
        textarea.className = "form-control";
        textarea.rows = 3;
        textarea.maxLength = 2000;
        textarea.name = "perguntas_auditoria";
        const remove = document.createElement("button");
        remove.className = "btn btn-outline-secondary audit-question-remove";
        remove.type = "button";
        remove.dataset.removeQuestion = "";
        remove.textContent = "×";
        control.append(textarea, remove);
        row.append(label, control);
        list.append(row);
        renumber();
        textarea.focus();
    }

    addButton.addEventListener("click", createQuestion);
    list.addEventListener("click", function (event) {
        const button = event.target.closest("[data-remove-question]");
        if (!button) {
            return;
        }
        const rows = list.querySelectorAll("[data-question-row]");
        if (rows.length > 1) {
            button.closest("[data-question-row]").remove();
            renumber();
        }
    });
    renumber();

    const typeSelect = document.getElementById("id_tipo_experiencia");
    const auditFields = Array.from(document.querySelectorAll("[data-audit-only]"));
    const evaluationFields = Array.from(
        document.querySelectorAll("[data-evaluation-only]")
    );
    const coordinatedFields = Array.from(
        document.querySelectorAll("[data-coordinated-field]")
    );
    function clearControls(field) {
        field.querySelectorAll("input, textarea, select").forEach(function (control) {
            if (control.type === "checkbox" || control.type === "radio") {
                control.checked = false;
            } else {
                control.value = "";
            }
        });
    }

    function updateConditionalFields(clearHidden) {
        if (!typeSelect) {
            return;
        }
        const selectedOption = typeSelect.options[typeSelect.selectedIndex];
        const typeCode = selectedOption ? selectedOption.dataset.tipoCodigo : "";
        const isAudit = typeCode === "auditoria" || typeCode === "auditoria_coordenada";
        const isCoordinated = typeCode === "auditoria_coordenada";
        const isEvaluation = typeCode === "avaliacao_politica_publica";
        auditFields.forEach(function (field) {
            field.hidden = !isAudit;
            if (clearHidden && !isAudit) {
                clearControls(field);
            }
        });
        coordinatedFields.forEach(function (field) {
            field.hidden = !isCoordinated;
            if (clearHidden && !isCoordinated) {
                clearControls(field);
            }
        });
        evaluationFields.forEach(function (field) {
            field.hidden = !isEvaluation;
            if (clearHidden && !isEvaluation) {
                clearControls(field);
            }
        });
    }
    if (typeSelect) {
        typeSelect.addEventListener("change", function () {
            updateConditionalFields(true);
        });
        updateConditionalFields(false);
    }
})();
