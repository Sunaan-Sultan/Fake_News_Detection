document
  .getElementById("feedback-form")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission

    const feedbackText = document.getElementById("feedback-text").value;

    // Show loading spinner
    document.getElementById("loading-spinner").style.display = "block";

    fetch("http://localhost:5000/send_feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ feedback: feedbackText }),
    })
      .then((response) => {
        console.log("Response status:", response.status);
        return response.json();
      })
      .then((data) => {
        console.log("Data received:", data);
        document.getElementById("loading-spinner").style.display = "none";
        document.getElementById("feedback-result").textContent = data.status;
        document.getElementById("feedback-text").value = ""; // Clear the textarea
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("loading-spinner").style.display = "none";
        document.getElementById("feedback-result").textContent =
          "Error sending feedback.";
      })
      .finally(() => {
        // Hide loading spinner regardless of success or failure
        document.getElementById("loading-spinner").style.display = "none";
      });
  });

function goBack() {
  window.location.href = "results.html"; // Redirect to results.html
}
