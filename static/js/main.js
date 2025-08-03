// fashion-shop/static/js/main.js

// Function to handle adding items to cart
async function handleAddToCart(productId, quantity = 1) {
    try {
        const response = await fetch(FLASK_URLS.addToCart, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Identify as AJAX request
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message); // Replace with a nicer notification later
            updateCartCountDisplay(data.cart_count); // Update cart count in header
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('An error occurred. Please try again.');
    }
}

// Function to handle updating cart item quantity
async function handleUpdateCartItem(itemId, newQuantity) {
    try {
        const response = await fetch(FLASK_URLS.updateCart, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ item_id: itemId, quantity: newQuantity })
        });

        const data = await response.json();

        if (data.success) {
            // Update the displayed total and potentially individual item costs on the cart page
            const cartTotalElement = document.getElementById('cart-total');
            if (cartTotalElement) {
                cartTotalElement.innerText = data.cart_total.toFixed(2);
            }
            // Optionally, update the specific item's subtotal if displayed
            // alert(data.message); // For debugging, remove later
        } else {
            alert('Error updating cart: ' + data.message);
            // Revert quantity input if update failed (e.g., stock issue)
            const inputElement = document.querySelector(`input[data-item-id="${itemId}"]`);
            if (inputElement) {
                // This is tricky without knowing the previous valid state.
                // A full page reload or re-fetching cart might be simpler for now.
                window.location.reload();
            }
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        alert('An error occurred. Please try again.');
    }
}

// Function to handle removing items from cart
async function handleRemoveFromCart(itemId) {
    if (!confirm('Are you sure you want to remove this item?')) {
        return;
    }
    try {
        const response = await fetch(FLASK_URLS.removeFromCart, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ item_id: itemId })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message); // Replace with a nicer notification
            // Remove the item's row from the display
            const itemRow = document.getElementById(`cart-item-${itemId}`);
            if (itemRow) {
                itemRow.remove();
            }
            // Update cart total and count
            const cartTotalElement = document.getElementById('cart-total');
            if (cartTotalElement) {
                cartTotalElement.innerText = data.cart_total.toFixed(2);
            }
            updateCartCountDisplay(currentCartCount - 1); // Simple decrement, assumes one item removed
            // Or re-fetch the cart to get exact count: window.location.reload();
        } else {
            alert('Error removing item: ' + data.message);
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        alert('An error occurred. Please try again.');
    }
}

// Event listeners for Add to Cart buttons on product pages
document.addEventListener('click', function(event) {
    // UPDATED: Use event.target.closest() to find the parent button
    const removeButton = event.target.closest('.remove-from-cart-btn');
    if (removeButton) {
        const itemId = removeButton.dataset.itemId;
        if (itemId) {
            handleRemoveFromCart(itemId);
        }
    }

    // Keep the update and remove cart item listeners as they are used on the cart page
    const quantityInput = event.target.closest('.cart-quantity-input');
    if (quantityInput) {
        const itemId = quantityInput.dataset.itemId;
        const newQuantity = parseInt(quantityInput.value);
        if (itemId && !isNaN(newQuantity)) {
            handleUpdateCartItem(itemId, newQuantity);
        }
    }
});

// Event listeners for quantity changes in cart (retained for update functionality)
document.addEventListener('change', function(event) {
    if (event.target.classList.contains('cart-quantity-input')) {
        const itemId = event.target.dataset.itemId;
        const newQuantity = parseInt(event.target.value);
        if (itemId && !isNaN(newQuantity)) {
            handleUpdateCartItem(itemId, newQuantity);
        }
    }
});

// Event listeners for remove from cart buttons (retained for click functionality)
// fashion-shop/static/js/main.js (snippet)
document.addEventListener('click', function(event) {
    const removeButton = event.target.closest('.remove-from-cart-btn');
    if (removeButton) {
        const itemId = removeButton.dataset.itemId;
        if (itemId) {
            handleRemoveFromCart(itemId);
        }
    }
});