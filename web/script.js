
const API_URL = "http://127.0.0.1:8000";

let products = [];

const productList = document.getElementById("product-list");
const dateInput = document.getElementById("date");

const requestVersions = new Map();
const updateTimers = new Map();


// -------------------------------------
// Load products dynamically from backend
// -------------------------------------

async function loadProducts() {
    productList.textContent = "Loading products...";

    try {
        const response = await fetch(`${API_URL}/products`);

        if (!response.ok) {
            throw new Error(
                `Failed to load products: ${response.status}`
            );
        }

        products = await response.json();

        if (!Array.isArray(products)) {
            throw new Error("Invalid products response");
        }

        console.log("Loaded products:", products);

        if (products.length === 0) {
            productList.textContent = "No products available.";
            return;
        }

        renderProducts();

    } catch (error) {
        console.error("Error loading products:", error);

        productList.textContent =
            "Unable to load products. Check backend connection.";
    }
}


// -------------------------------------
// Price formatting
// -------------------------------------

function formatPrice(price) {
    return `$${Number(price).toFixed(2)}`;
}


// -------------------------------------
// Render product rows
// -------------------------------------

function renderProducts() {
    productList.innerHTML = "";

    requestVersions.clear();

    updateTimers.forEach((timer) => clearTimeout(timer));
    updateTimers.clear();

    products.forEach((product) => {
        const min = Number(product.min);
        const max = Number(product.max);
        const price = Number(product.price);

        if (
            !product.name ||
            !Number.isFinite(min) ||
            !Number.isFinite(max) ||
            !Number.isFinite(price) ||
            min > max
        ) {
            console.warn("Skipping invalid product:", product);
            return;
        }

        const safePrice = Math.min(max, Math.max(min, price));

        const row = document.createElement("article");
        row.className = "product-row";
        row.dataset.product = product.name;

        row.innerHTML = `
            <h2 class="product-name"></h2>

            <div class="price-control">
                <div class="price-readout">
                    <span class="price-value"></span>
                    <span class="price-range"></span>
                </div>

                <input
                    class="price-slider"
                    type="range"
                    step="0.01"
                >
            </div>

            <div
                class="prediction"
                aria-live="polite"
            >
                <span class="prediction-value">--</span>
                <span class="prediction-unit">units</span>
                <span class="prediction-status">Loading</span>
            </div>
        `;

        const nameElement = row.querySelector(".product-name");
        const slider = row.querySelector(".price-slider");
        const priceValue = row.querySelector(".price-value");
        const priceRange = row.querySelector(".price-range");
        const predictionElement = row.querySelector(".prediction");

        nameElement.textContent = product.name;

        slider.min = min;
        slider.max = max;
        slider.value = safePrice;
        slider.disabled = min === max;

        slider.setAttribute(
            "aria-label",
            `${product.name} price`
        );

        predictionElement.setAttribute(
            "aria-label",
            `${product.name} predicted sales`
        );

        priceValue.textContent = formatPrice(safePrice);

        priceRange.textContent =
            `${formatPrice(min)}–${formatPrice(max)}`;

        slider.addEventListener("input", () => {
            priceValue.textContent = formatPrice(slider.value);

            const productName = row.dataset.product;

            clearTimeout(updateTimers.get(productName));

            updateTimers.set(
                productName,
                setTimeout(() => {
                    fetchPrediction(row);
                    updateTimers.delete(productName);
                }, 180)
            );
        });

        productList.appendChild(row);

        fetchPrediction(row);
    });
}


// -------------------------------------
// Fetch prediction from FastAPI
// -------------------------------------

async function fetchPrediction(row) {
    const product = row.dataset.product;

    const slider = row.querySelector(".price-slider");
    const value = row.querySelector(".prediction-value");
    const status = row.querySelector(".prediction-status");

    const version =
        (requestVersions.get(product) || 0) + 1;

    requestVersions.set(product, version);

    status.textContent = "Updating";
    row.classList.add("is-updating");

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                product: product,
                price: Number(slider.value),
                date: dateInput.value
            })
        });

        if (!response.ok) {
            const errorMessage = await response.text();

            throw new Error(
                `Prediction failed: ${errorMessage}`
            );
        }

        const data = await response.json();

        // Ignore outdated requests
        if (requestVersions.get(product) !== version) {
            return;
        }

        const prediction = Number(data.predicted_sales);

        if (!Number.isFinite(prediction)) {
            throw new Error("Invalid prediction response");
        }

        value.textContent = Math.max(0, prediction).toFixed(2);

        status.textContent = "Updated";

    } catch (error) {
        if (requestVersions.get(product) !== version) {
            return;
        }

        console.error(
            `Prediction error for ${product}:`,
            error
        );

        status.textContent = "Unavailable";
        value.textContent = "–";

    } finally {
        if (requestVersions.get(product) === version) {
            row.classList.remove("is-updating");
        }
    }
}


// -------------------------------------
// Handle prediction date changes
// -------------------------------------

function initializeDate() {
    const now = new Date();

    const localDate = new Date(
        now.getTime() - now.getTimezoneOffset() * 60000
    );

    dateInput.value = localDate.toISOString().slice(0, 10);
}

dateInput.addEventListener("change", () => {
    updateTimers.forEach((timer) => clearTimeout(timer));
    updateTimers.clear();

    productList
        .querySelectorAll(".product-row")
        .forEach((row) => {
            fetchPrediction(row);
        });
});


// -------------------------------------
// Initialize application
// -------------------------------------

async function initializeApp() {
    initializeDate();

    await loadProducts();
}

initializeApp();
