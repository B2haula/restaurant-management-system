"use strict";

const pageDefinitions = {
    "category-form": {
        listId: "category-list",
        key: "restaurant_categories",
        fields: ["category_name"],
        headings: ["Category ID", "Category Name"],
        idField: "category_id",
        idHeading: "Category ID",
        submitLabel: "Save Category",
        resetLabel: "Clear"
    },
    "menu-form": {
        listId: "menu-list",
        key: "restaurant_menus",
        fields: ["menu_name", "price", "availability", "category_id"],
        headings: ["Menu Name", "Price", "Availability", "Category ID"],
        idField: "menu_id",
        idHeading: "Menu ID",
        submitLabel: "Save Menu",
        resetLabel: "Clear"
    },
    "menu-item-form": {
        listId: "menu-item-list",
        key: "restaurant_menu_items",
        fields: ["menu_item", "menu_id"],
        headings: ["Menu Item", "Menu ID"],
        idField: "menuitem_id",
        idHeading: "Menu Item ID",
        submitLabel: "Save Menu Item",
        resetLabel: "Clear"
    },
    "order-form": {
        listId: "order-list",
        key: "restaurant_orders",
        fields: ["order_type", "customer", "menu_id", "order_status", "amount"],
        headings: ["Order Type", "Customer", "Menu ID", "Order Status", "Amount"],
        submitLabel: "Save Order",
        resetLabel: "Clear"
    },
    "table-form": {
        listId: "table-list",
        key: "restaurant_tables",
        fields: ["location", "tablee_status", "capacity"],
        headings: ["Location", "Table Status", "Capacity"],
        idField: "table_id",
        idHeading: "Table ID",
        submitLabel: "Save Table",
        resetLabel: "Clear"
    },
    "waiter-form": {
        listId: "waiter-list",
        key: "restaurant_waiters",
        fields: ["waiter_name", "birth_year", "shift", "contact", "address", "number_of_tables_assigned"],
        headings: ["Waiter Name", "Date of Birth", "Shift", "Contact", "Address", "Number of Tables Assigned"],
        idField: "waiter_id",
        idHeading: "Waiter ID",
        submitLabel: "Save Waiter",
        resetLabel: "Clear"
    },
    "order-details-form": {
        listId: "order-details-list",
        key: "restaurant_order_details",
        fields: ["order_id", "quantity"],
        headings: ["Order ID", "Quantity"],
        idField: "orderdetails_id",
        idHeading: "Order Details ID",
        submitLabel: "Save Order Details",
        resetLabel: "Clear"
    },
    "waiter-table-form": {
        listId: "waiter-table-list",
        key: "restaurant_waiter_tables",
        fields: ["waiter_id", "tablee_id"],
        headings: ["Waiter ID", "Table ID"],
        idField: "waitertablee_id",
        idHeading: "WaiterTablee ID",
        submitLabel: "Save WaiterTablee",
        resetLabel: "Clear"
    }
};

function readRecords(key) {
    try {
        const records = JSON.parse(localStorage.getItem(key));
        return Array.isArray(records) ? records : [];
    } catch {
        return [];
    }
}

function saveRecords(key, records) {
    try {
        localStorage.setItem(key, JSON.stringify(records));
    } catch {
        window.alert("This browser could not save the record. Please allow local storage and try again.");
    }
}

const standaloneHeader = document.querySelector("body > header");
if (standaloneHeader) {
    standaloneHeader.classList.add("navbar", "navbar-header", "navbar-header-transparent", "border-bottom");
    standaloneHeader.querySelector("h1")?.classList.add("navbar-brand", "fw-bold", "mb-0");
}

document.querySelector("main")?.classList.add("container-fluid", "py-4");
document.querySelectorAll("main > h2").forEach((heading) => {
    heading.classList.add("page-title", "mb-3");
});
document.querySelectorAll("form[id]").forEach((form) => {
    form.classList.add("card", "p-3");
    form.querySelectorAll("input, select").forEach((control) => {
        control.classList.add(control.tagName === "SELECT" ? "form-select" : "form-control");
    });
    form.querySelector('button[type="submit"]')?.classList.add("btn", "btn-primary");
    form.querySelector('button[type="reset"]')?.classList.add("btn", "btn-secondary");
});
document.querySelectorAll("table").forEach((table) => {
    table.classList.add("table", "table-hover", "align-middle");
});
document.querySelectorAll(".actions").forEach((actions) => {
    actions.classList.add("d-flex", "align-items-center", "gap-2");
});

function formatValue(field, value) {
    if (field === "price" || field === "amount") {
        const amount = Number(value);
        return Number.isFinite(amount) ? amount.toFixed(2) : value;
    }

    if (field === "availability" || field === "order_status" ||
        field === "tablee_status" || field === "shift") {
        return value.charAt(0).toUpperCase() + value.slice(1);
    }

    return value;
}

function makeButton(action, index, className = "") {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.classList.add("btn", "btn-sm", action === "edit" ? "btn-warning" : "btn-danger");
    button.dataset.action = action;
    button.dataset.index = String(index);

    const label = action === "edit" ? "Edit record" : "Delete record";
    button.title = label;
    button.setAttribute("aria-label", label);

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "16");
    svg.setAttribute("height", "16");
    svg.setAttribute("aria-hidden", "true");
    svg.style.display = "block";

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    if (action === "edit") {
        path.setAttribute("d", "M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L8 18l-4 1 1-4Z");
    } else {
        path.setAttribute(
            "d",
            "M3 6h18M8 6V3h8v3m3 0-1 15H6L5 6m5 4v7m4-7v7"
        );
    }
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "currentColor");
    path.setAttribute("stroke-width", "2");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("stroke-linejoin", "round");

    svg.appendChild(path);
    button.appendChild(svg);
    return button;
}

document.querySelectorAll("form[id]").forEach((form) => {
    const definition = pageDefinitions[form.id];
    const list = definition ? document.getElementById(definition.listId) : null;

    if (!definition || !list) {
        return;
    }

    let editingIndex = null;
    const submitButton = form.querySelector('button[type="submit"]');
    const resetButton = form.querySelector('button[type="reset"]');
    let statusMessage = document.getElementById(`${form.id}-status`);

    if (!statusMessage) {
        statusMessage = document.createElement("p");
        statusMessage.id = `${form.id}-status`;
        statusMessage.className = "alert alert-success py-2 d-none";
        statusMessage.setAttribute("role", "status");
        statusMessage.setAttribute("aria-live", "polite");
        list.closest("table").before(statusMessage);
    }

    function render() {
        const records = readRecords(definition.key);
        if (definition.idField) {
            records.forEach((record, index) => {
                if (!record[definition.idField]) {
                    const highestId = records.reduce((highest, item) => {
                        const numericId = Number(item[definition.idField]);
                        return Number.isFinite(numericId) ? Math.max(highest, numericId) : highest;
                    }, 0);
                    record[definition.idField] = highestId + 1;
                }
            });
            saveRecords(definition.key, records);
        }
        list.replaceChildren();

        records.forEach((record, index) => {
            const row = document.createElement("tr");

            if (definition.idField) {
                const idCell = document.createElement("td");
                idCell.textContent = record[definition.idField] || String(index + 1);
                row.appendChild(idCell);
            }

            definition.fields.forEach((field) => {
                const cell = document.createElement("td");
                cell.textContent = formatValue(field, record[field] ?? "");
                row.appendChild(cell);
            });

            const actionsCell = document.createElement("td");
            const actions = document.createElement("div");
            actions.className = "actions";
            actions.appendChild(makeButton("edit", index, "edit-btn icon-btn"));
            actions.appendChild(makeButton("delete", index, "delete-btn icon-btn"));
            actionsCell.appendChild(actions);
            row.appendChild(actionsCell);

            list.appendChild(row);
        });
    }

    function resetEditing() {
        editingIndex = null;
        if (submitButton) submitButton.textContent = definition.submitLabel;
        if (resetButton) resetButton.textContent = definition.resetLabel;
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        const record = {};
        definition.fields.forEach((field) => {
            const input = form.elements.namedItem(field);
            record[field] = input ? input.value.trim() : "";
        });

        const records = readRecords(definition.key);
        const actionWasUpdate = editingIndex !== null;

        if (definition.idField) {
            if (editingIndex === null) {
                const highestId = records.reduce((highest, item) => {
                    const numericId = Number(item[definition.idField]);
                    return Number.isFinite(numericId) ? Math.max(highest, numericId) : highest;
                }, 0);
                record[definition.idField] = highestId + 1;
            } else {
                record[definition.idField] = records[editingIndex][definition.idField]
                    || (editingIndex + 1);
            }
        }

        if (editingIndex === null) {
            records.push(record);
        } else {
            records[editingIndex] = record;
        }

        saveRecords(definition.key, records);
        form.reset();
        resetEditing();
        render();
        statusMessage.textContent = actionWasUpdate
            ? "Record updated successfully."
            : "Record saved successfully.";
        statusMessage.classList.remove("d-none");
    });

    form.addEventListener("reset", () => {
        window.setTimeout(resetEditing, 0);
    });

    list.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) {
            return;
        }

        const index = Number(button.dataset.index);
        const records = readRecords(definition.key);
        const record = records[index];

        if (!record) {
            return;
        }

        if (button.dataset.action === "delete") {
            if (!window.confirm("Delete this record?")) {
                return;
            }

            records.splice(index, 1);
            saveRecords(definition.key, records);
            if (editingIndex === index) {
                form.reset();
                resetEditing();
            }
            render();
            statusMessage.textContent = "Record deleted successfully.";
            statusMessage.classList.remove("d-none");
            return;
        }

        if (button.dataset.action === "edit") {
            editingIndex = index;
            definition.fields.forEach((field) => {
                const input = form.elements.namedItem(field);
                if (input) input.value = record[field] ?? "";
            });
            if (submitButton) submitButton.textContent = "Update Record";
            form.scrollIntoView({ behavior: "smooth", block: "start" });
            const firstInput = form.querySelector("input, select");
            if (firstInput) firstInput.focus();
        }
    });

    render();
});
