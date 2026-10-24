const products = [
    { name: "Salmon", min: 140, max: 220, price: 178 },
    { name: "Cod", min: 120, max: 190, price: 154 },
    { name: "Haddock", min: 95, max: 155, price: 126 },
    { name: "Herring", min: 45, max: 85, price: 67 },
    { name: "Mackerel", min: 65, max: 110, price: 88 },
    { name: "Mussels", min: 55, max: 95, price: 73 },
    { name: "Shrimp", min: 160, max: 260, price: 212 },
    { name: "Trout", min: 110, max: 175, price: 139 }
];

const productList = document.getElementById("product-list");
const dateInput = document.getElementById("date");
const requestVersions = new Map();
const updateTimers = new Map();

function renderProducts() {
    productList.innerHTML = products.map((product) => `
        <article class="product-row" data-product="${product.name}">
            <h2 class="product-name">${product.name}</h2>
            <div class="price-control">
                <div class="price-readout">
                    <span class="price-value">$${product.price}</span>
                    <span class="price-range">$${product.min}–$${product.max}</span>
                </div>
                <input
                    class="price-slider"
                    type="range"
                    min="${product.min}"
                    max="${product.max}"
                    step="1"
                    value="${product.price}"
                    aria-label="${product.name} price"
                >
            </div>
            <div class="prediction" aria-live="polite" aria-label="${product.name} predicted sales">
                <span class="prediction-value">--</span>
                <span class="prediction-unit">units</span>
                <span class="prediction-status">Loading</span>
            </div>
        </article>
    `).join("");

    productList.querySelectorAll(".product-row").forEach((row) => {
        const slider = row.querySelector(".price-slider");
        const priceValue = row.querySelector(".price-value");

        slider.addEventListener("input", () => {
            priceValue.textContent = `$${slider.value}`;
            clearTimeout(updateTimers.get(row.dataset.product));
            updateTimers.set(row.dataset.product, setTimeout(() => {
                fetchPrediction(row);
            }, 180));
        });

        fetchPrediction(row);
    });
}

async function fetchPrediction(row) {
    const product = row.dataset.product;
    const slider = row.querySelector(".price-slider");
    const value = row.querySelector(".prediction-value");
    const status = row.querySelector(".prediction-status");
    const version = (requestVersions.get(product) || 0) + 1;
    requestVersions.set(product, version);
    status.textContent = "Updating";
    row.classList.add("is-updating");

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product,
                price: Number(slider.value),
                date: dateInput.value
            })
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        if (requestVersions.get(product) !== version) return;

        value.textContent = data.predicted_sales.toFixed(2);
        status.textContent = "Updated";
    } catch (error) {
        if (requestVersions.get(product) !== version) return;
        console.error(error);
        status.textContent = "Unavailable";
        if (value.textContent === "--") value.textContent = "–";
    } finally {
        if (requestVersions.get(product) === version) {
            row.classList.remove("is-updating");
        }
    }
}

dateInput.value = new Date().toISOString().slice(0, 10);
dateInput.addEventListener("change", () => {
    productList.querySelectorAll(".product-row").forEach(fetchPrediction);
});

renderProducts();