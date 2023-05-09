$(document).ready(function() {
	$('#search-input').on('input', function() {
		var query = $(this).val().trim();
		if (query.length >= 0) {
			$.ajax({
				type: 'POST',
				url: '/search_live',
				data: { query: query },
				dataType: 'json',
				success: function(data) {
					if (data.results.length > 0) {
						var results = '';
						data.results.forEach(function(result) {
							results += '<li><a href="/detail/' + result[0] + '">' + result[2] + '</a></li>';
						});
						$('#search-results ul').html(results);
					} else {
						$('#search-results ul').html('No results found.');
					}
				},
				error: function() {
					$('#search-results ul').html('Error searching.');
				}
			});
		} else {
			$('#search-results ul').html('');
		}
	});
});