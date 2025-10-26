/*
пример. у нулевого формсета ContractComposition такие поля:
composition-0-product
composition-0-total_volume
composition-0-cost

у empty_form формсета (который мы копируем при нажатии на кнопку "Добавить строку") такие поля:
composition-__prefix__-product
composition-__prefix__-total_volume
composition-__prefix__-cost

composition - это formsetPrefix

0, 1, 2, ... 999 - это индекс формсета. 
для пустого формсета используется магическое слово __prefix__, с которым Django отдаёт нам пустой формсет
*/

document.addEventListener("DOMContentLoaded", function () {
    const formsetContainer = document.getElementById("formset-container");
    const addButton = document.getElementById("add-form");
    const emptyFormTemplate = document.getElementById("empty-form-template").innerHTML;

    function updateElementIndex(el, formsetPrefix, index) {
        const idRegex = new RegExp(formsetPrefix + "-(\\d+|__prefix__)-");
        const replacement = formsetPrefix + "-" + index + "-";
        if (el.hasAttribute("for")) {
            el.setAttribute("for", el.getAttribute("for").replace(idRegex, replacement));
        }
        if (el.id) {
            el.id = el.id.replace(idRegex, replacement);
        }
        if (el.name) {
            el.name = el.name.replace(idRegex, replacement);
        }
    }

    function updateFormIndices(formsetPrefix) {
        const forms = formsetContainer.querySelectorAll(".formset-form");
        forms.forEach((form, i) => {
            form.querySelectorAll("input, select, textarea, label").forEach(el => {
                updateElementIndex(el, formsetPrefix, i);
            });
        });
        document.getElementById("id_" + formsetPrefix + "-TOTAL_FORMS").value = forms.length;
    }

    addButton.addEventListener("click", function () {
        const formsetPrefix = formsetContainer.querySelector("input[name$='-TOTAL_FORMS']").name.split("-")[0];
        const newForm = document.createElement("div");
        newForm.innerHTML = emptyFormTemplate;
        formsetContainer.appendChild(newForm.firstElementChild);
        updateFormIndices(formsetPrefix);
    });

    formsetContainer.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-form")) {
            e.target.closest(".formset-form").remove();
            const formsetPrefix = formsetContainer.querySelector("input[name$='-TOTAL_FORMS']").name.split("-")[0];
            updateFormIndices(formsetPrefix);
        }
    });
});
