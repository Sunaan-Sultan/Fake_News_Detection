document.addEventListener("DOMContentLoaded", function () {
  const newsTextElement = document.getElementById("news-text");
  const predictionResultElement = document.getElementById("prediction-result");
  const evidenceListElement = document.getElementById("evidence-list");

  // Get saved input news and prediction from localStorage
  const inputText = localStorage.getItem("inputText");
  const prediction = localStorage.getItem("prediction");

  // Extract the first line of the user's input text
  let firstLine = inputText.split("\n")[0];

  // Truncate the first line if too long
  if (firstLine.length > 150) {
    firstLine = firstLine.substring(0, 150) + "...";
  }

  // Display the first line of input text
  newsTextElement.textContent = `"${firstLine}"`;

  // Clear previous classes before applying a new one
  newsTextElement.classList.remove(
    "fake-news",
    "mostly-false",
    "half-true",
    "mostly-true",
    "real-news"
  );

  // Function to create an image element
  function createImage(src, alt) {
    const img = document.createElement("img");
    img.src = src;
    img.alt = alt;
    img.style.maxWidth = "100px";
    img.style.height = "auto";
    return img;
  }

  // Display prediction result as an image and apply appropriate styles
  if (prediction === "False News") {
    predictionResultElement.appendChild(
      createImage("img/false.png", "False News")
    );
    newsTextElement.classList.add("fake-news");
  } else if (prediction === "Mostly False") {
    predictionResultElement.appendChild(
      createImage("img/mostly_false.png", "Mostly False")
    );
    newsTextElement.classList.add("mostly-false");
  } else if (prediction === "Half True") {
    predictionResultElement.appendChild(
      createImage("img/half_true.png", "Half True")
    );
    newsTextElement.classList.add("half-true");
  } else if (prediction === "Mostly True") {
    predictionResultElement.appendChild(
      createImage("img/mostly_true.png", "Mostly True")
    );
    newsTextElement.classList.add("mostly-true");
  } else if (prediction === "True News") {
    predictionResultElement.appendChild(
      createImage("img/true.png", "True News")
    );
    newsTextElement.classList.add("real-news");
  } else {
    predictionResultElement.textContent = "Unknown Prediction";
    predictionResultElement.style.color = "black";
  }

  // Fetch evidence articles from localStorage
  const evidence = JSON.parse(localStorage.getItem("evidence"));
  if (evidence) {
    evidence.forEach((item) => {
      const listItem = document.createElement("li");
      const anchor = document.createElement("a");
      anchor.href = item.url;
      anchor.textContent = item.title;
      anchor.target = "_blank";
      listItem.appendChild(anchor);
      listItem.appendChild(document.createTextNode(" - " + item.snippet));
      evidenceListElement.appendChild(listItem);
    });
  }

  // Feedback button functionality
  document
    .getElementById("feedback-button")
    .addEventListener("click", function () {
      window.location.href = "feedback.html";
    });
});
