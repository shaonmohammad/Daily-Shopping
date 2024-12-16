function handleAddToCart(productId) {
  fetch("/add_to_cart/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({ product_id: productId }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error("Something went wrong!");
    })
    .then((data) => {
      showSuccessModal(data.message);
    })
    .catch((error) => {
      console.error(error);
      alert("Failed to add product to cart.");
    });
}

function showSuccessModal(message) {
  const modalHTML = `
    <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="successModalLabel">Success</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ${message}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" id="refreshButton">OK</button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML("beforeend", modalHTML);

  const successModal = new bootstrap.Modal(document.getElementById("successModal"));
  successModal.show();

  document.getElementById("refreshButton").addEventListener("click", () => {
    location.reload();
  });
}

function getCSRFToken() {
  const cookies = document.cookie.split("; ");
  for (let cookie of cookies) {
    const [name, value] = cookie.split("=");
      if (name === "csrftoken") {
        console.log(value)
        return decodeURIComponent(value);
    }
  }
  return null;
}
