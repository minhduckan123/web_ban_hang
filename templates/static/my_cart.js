function handlePayAllResult(result) {
    if (result.status === 'Fail') {
      alert('Payment failed.');
    } else {
      alert('Payment successful.');
      window.location.href = '/my_cart';
    }
  };
