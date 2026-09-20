const button = document.getElementById("testButton");
const responseBox = document.getElementById("response");

button.addEventListener("click", async () => {

    button.disabled = true;
    button.textContent = "Sending...";

    try {
        const response = await fetch("/api");
        const data = await response.json();

        responseBox.textContent =
            JSON.stringify(data, null, 2);

    } catch (error) {

        responseBox.textContent =
            "Request failed: " + error;

    } finally {

        button.disabled = false;
        button.textContent = "Send Request";
    }
});