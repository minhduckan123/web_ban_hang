$(document).ready(function() {
    var bookId = $('#book-price').data('book-id');
    var bookPrice = parseFloat($('#book-price').text());
    $('#book-total').text(bookPrice);
    $('#book-quantity').on('input', function() {
        var quantity = $(this).val();
        var total = quantity * bookPrice;
        $('#book-total').text(total.toFixed(2));
    });
    $('#add-to-cart-btn').on('click', function() {
        var quantity = $('#book-quantity').val();
        var quantityInput = document.getElementById('book-quantity');
        var maxQuantity = parseInt(quantityInput.getAttribute('max'), 10);
        if (quantity < 1) {
            alert('Số lượng phải lớn hơn 0.');
            quantityInput.value = 1;
            return false
        } else if (quantity > maxQuantity) {
            alert('Số lượng vượt quá số lượng tối đa cho phép.');
            quantityInput.value = maxQuantity;
            return false
        }
        $.ajax({
            type: 'POST',
            url: '/add_to_cart',
            data: { book_id: bookId, quantity: quantity },
            success: function(data) {
                alert(data['status']);
            },
            error: function() {
                alert('Error adding to cart!');
            }
        });
    });
});