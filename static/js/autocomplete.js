// author: darkryder - https://github.com/darkryder/

// set type variable in window js variable
// #searching is a png for searching
// #responsebox is the box with the answers

$(document).ready(function(){
	var search_results = {};
	var responsebox = $("#responsebox");
	var responses = $("#responses")[0];

	var category = window.item_category_to_autosearch;

	responsebox.fadeOut(0)



	function show_response(data){
		$("#searching").hide();
		if (data.length == 0) {
			responsebox.fadeOut(100)
		}
		else {
			responses.innerHTML = "";
			for (var i = 0; i < data.length; i++) {
				responses.innerHTML += '<a href="#" style="color:black" \
										class="response" data-toggle="modal"\
										data-remote="true" data-url="'
										+ data[i]['url'] + '"><b>  '
										+ data[i]['itemname'] + '</b></a><br />'
			};
			// attach the listener again
			$(".response").click(function(){
				$("#base-confirmation-modal").modal('hide');
				$("#base-confirmation-modal").modal('show');
				$("#base-confirmation-modal").load($(this).data().url);
			});
			responsebox.fadeIn(500);
		}

	}
	var timer;
	$("#item_name_field").on('input paste', function(){
		var value = this.value;
		if (value === ""){
			responsebox.fadeOut(100);
			return;
		}
		if (search_results[value] === undefined)
		{
			$("#searching").show();
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