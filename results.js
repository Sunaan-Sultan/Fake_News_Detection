document.addEventListener("DOMContentLoaded", function () {
  const newsTextElement = document.getElementById("news-text");
  const predictionResultElement = document.getElementById("prediction-result");
  const evidenceListElement = document.getElementById("evidence-list");

  // Get saved input news and prediction from localStorage
  const inputText = localStorage.getItem("inputText");
  const prediction = localStorage.getItem("prediction");

  // Extract the first line of the user's input text
  let firstLine = inputText.split("\n")[0]; // Ensure first line is extracted even if there are multiple line breaks

  // Truncate the first line if too long (optional)
  if (firstLine.length > 150) {
    // Adjust the character limit if needed
    firstLine = firstLine.substring(0, 150) + "...";
  }

  // Display the first line of input text
  newsTextElement.textContent = `"${firstLine}"`;

  // Display prediction result and set text color based on prediction
  if (prediction === "FAKE") {
    predictionResultElement.textContent = "Fake News";
    predictionResultElement.style.color = "red"; // Set text color to red for FAKE news
  } else if (prediction === "REAL") {
    predictionResultElement.textContent = "Real News";
    predictionResultElement.style.color = "green"; // Set text color to green for REAL news
  } else {
    predictionResultElement.textContent = prediction;
    predictionResultElement.style.color = "black"; // Default color for other cases
  }

  // Fetch evidence articles from localStorage
  const evidence = JSON.parse(localStorage.getItem("evidence"));
  if (evidence) {
    evidence.forEach((item) => {
      const listItem = document.createElement("li");
      const anchor = document.createElement("a");
      anchor.href = item.url;
      anchor.textContent = item.title;
      anchor.target = "_blank"; // Ensure the link opens in a new tab
      listItem.appendChild(anchor);
      listItem.appendChild(document.createTextNode(" - " + item.snippet));
      evidenceListElement.appendChild(listItem);
    });
  }

  // Feedback button functionality
  document
    .getElementById("feedback-button")
    .addEventListener("click", function () {
      window.location.href = "feedback.html"; // Redirect to feedback.html on button click
    });
});
