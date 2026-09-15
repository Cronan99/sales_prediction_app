async function predictSales() {
    const product = document.getElementById("product").value;
    const price = parseFloat(document.getElementById("price").value);
    const date = document.getElementById("date").value;

    const result = document.getElementById("result");

    if (!product || isNaN(price) || !date) {
        result.textContent = "Please fill in all fields.";
        return;
    }

    result.textContent = "Predicting...";

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/predict",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product: product,
                    price: price,
                    date: date
                })
            }
        );

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }

        const data = await response.json();

        result.textContent =
            `Predicted sales: ${data.predicted_sales}`;

    } catch (error) {
        console.error(error);
        result.textContent = "Prediction failed.";
    }
}