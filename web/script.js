async function predictSales() {
    const product = document.getElementById("product").value;
    const price = parseFloat(document.getElementById("price").value);
    const date = document.getElementById("date").value;

    const resultElement = document.getElementById("result");

    // Basic validation
    if (!product || isNaN(price) || !date) {
        resultElement.textContent = "Please fill in all fields.";
        return;
    }

    try {
        resultElement.textContent = "Calculating...";

        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                product: product,
                price: price,
                date: date
            })
        });

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const data = await response.json();

        resultElement.textContent =
            `Predicted sales: ${data.predicted_sales.toFixed(2)}`;

    } catch (error) {
        console.error(error);

        resultElement.textContent =
            "Could not get prediction from server.";
    }
}