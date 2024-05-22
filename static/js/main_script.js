let one_period_btn = document.getElementById("one_period");
let list_period_btn = document.getElementById("list_periods");
let categories_btn = document.getElementById("categories");

let transfers = document.getElementById("transfers");
let periods_tau = document.getElementById("periods_tau");
let hlOperations = document.getElementById("HLoperations")
let category = document.getElementById("categories_input")

let form = document.getElementById("build_form");

one_period_btn.addEventListener("click", (event) => {
    one_period_btn.classList.add("selected-type");
    list_period_btn.classList.remove("selected-type");
    categories_btn.classList.remove("selected-type");

    periods_tau.classList.add("disabled");
    transfers.classList.remove("disabled");
    hlOperations.classList.remove("disabled")
    category.classList.add("disabled");

    form.action = "/build_one_period";
});

list_period_btn.addEventListener("click", (event) => {
    one_period_btn.classList.remove("selected-type");
    list_period_btn.classList.add("selected-type");
    categories_btn.classList.remove("selected-type");

    periods_tau.classList.remove("disabled");
    transfers.classList.remove("disabled");
    hlOperations.classList.remove("disabled")
    category.classList.add("disabled");

    form.action = "/build_list_period";
});

categories_btn.addEventListener("click", (event) => {
    one_period_btn.classList.remove("selected-type");
    list_period_btn.classList.remove("selected-type");
    categories_btn.classList.add("selected-type");

    periods_tau.classList.remove("disabled");
    transfers.classList.remove("disabled");
    hlOperations.classList.add("disabled")
    category.classList.remove("disabled");
    form.action = "/build_categories";
});

window.addEventListener("load", () => {
    list_period_btn.click();
});