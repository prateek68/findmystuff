// author: darkryder - https://github.com/darkryder/

$(document).ready(function(){
	var search_results = {};
	var responses = $("#responses")[0];

	var category = window.item_category_to_autosearch;

	function show_response(data){
		if (data.length == 0) {
			$("#item_name_field").popover('destroy');
		}
		else {
			var a = "<b>Did you mean?</b><br /><ul>"
			for (var i = 0; i < data.length; i++) {
				a += '<li><a href="#" style="color:black" \
										class="response" data-toggle="modal"\
										data-remote="true" data-url="'
										+ data[i]['url'] + '"><b>  '
										+ data[i]['itemname'] + '</b></a>'
			};
			a += '</ul>';
			$("#item_name_field").popover('destroy');
			$("#item_name_field").popover({
				content: a,
				focus: false	,
				html: true
			}).popover("show");

			// attach the listener again
			$(".response").click(function(){
				$("#base-confirmation-modal").modal('hide');
				$("#base-confirmation-modal").modal('show');
				$("#base-confirmation-modal").load($(this).data().url);
			});
		}
	}
	var timer;
	$("#item_name_field").on('input paste', function(){
		var value = this.value;
		if (value.trim() == ""){
			$("#item_name_field").popover('destroy');
			return;
		}
		if (search_results[value] === undefined)
		{
			clearTimeout(timer);
			var ms = 300;
			timer = setTimeout(function(){
				$.get("/autocomplete/search/", { "query": value,
				  "type": category
				}, function(data){
					search_results[value] = data;
					show_response(data);
				})
			}, ms);
		}
		else
		{
			show_response(search_results[value]);
		}

	})
});