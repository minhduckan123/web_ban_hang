// Lưu trạng thái hiện tại của nút thêm sách
var isAddingBook = true;

// Lắng nghe sự kiện click của nút thêm sách
$('#add-book-btn').on('click', function() {
  // Lấy ID của sách và ID của user từ dữ liệu của nút thêm sách
  var bookId = $(this).data('book-id');

  // Kiểm tra trạng thái hiện tại của nút thêm sách
  if (isAddingBook) {
    // Nếu đang ở trạng thái "Thêm sách", thực hiện yêu cầu POST để thêm sách vào user_book
    $.ajax({
      type: 'POST',
      url: '/add_to_cart',
      data: { book_id: bookId },
      success: function() {
        alert('Book added to cart!');
        // Đổi trạng thái của nút thành "Remove from cart"
        $('#add-book-btn').text('Remove book from cart');
        isAddingBook = false;
      },
      error: function() {
        alert('Error adding book to cart!');
        // Xử lý lỗi
      }
    });
  } else {
    // Nếu đang ở trạng thái "Xóa sách", thực hiện yêu cầu POST để xóa sách khỏi user_book
    $.ajax({
      type: 'POST',
      url: '/remove_from_cart',
      data: { book_id: bookId },
      success: function() {
        alert('Book removed from cart!');
        // Đổi trạng thái của nút thành "Thêm sách"
        $('#add-book-btn').text('Thêm sách');
        isAddingBook = true;
      },
      error: function() {
        alert('Error removing book from cart!');
        // Xử lý lỗi
      }
    });
  }
});