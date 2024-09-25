document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("news-form");
  const newsTextInput = document.getElementById("news-text");
  const loadingSpinner = document.getElementById("loading-spinner");

  // Retrieve text from local storage on page load
  const savedText = localStorage.getItem("savedNewsText");
  if (savedText) {
    newsTextInput.value = savedText;
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("text", newsTextInput.value);

    // Show loading spinner
    loadingSpinner.style.display = "block";

    setTimeout(async function () {
      try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Failed to fetch prediction");
        }

        const data = await response.json();

        // Save prediction result and input news to localStorage
        localStorage.setItem("prediction", data.prediction);
        localStorage.setItem("inputText", newsTextInput.value);
        localStorage.setItem("evidence", JSON.stringify(data.evidence));

        // Redirect to results.html
        window.location.href = "results.html";
      } catch (error) {
        console.error("Error:", error);
        localStorage.setItem("prediction", "Something went wrong");
        window.location.href = "results.html";
      } finally {
        loadingSpinner.style.display = "none";
      }
    }, 3000);
  });

  // Save text to local storage when input changes
  newsTextInput.addEventListener("input", function () {
    localStorage.setItem("savedNewsText", newsTextInput.value);
  });
});
