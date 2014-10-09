// author: darkryder - https://github.com/darkryder/

$(document).ready(function(){
	$("#searching_text").hide();
	var search_results = {};

	function include(arr,obj) {
		return (arr.indexOf(obj) != -1);
	}

	function handle_search(data){
		$("#searching_text").hide();
		var elem = $(".result");
		for(var i = 0; i < elem.length; i++)
		{
			if (include(data, elem[i].id)){
				$("#" + elem[i].id).fadeIn(0);
			}
			else {
				$("#" + elem[i].id).fadeOut(0);
			}
		}
	}
	var timer;
	$("#search").on('input paste', function(){
		var value = this.value;
		var token = $('input[name="csrfmiddlewaretoken"]')[0].value
		if (value === ""){
			$(".result").fadeIn(0);
			return;
		}
		if (search_results[value] === undefined)
		{
			$("#searching_text").show();
			clearTimeout(timer);
			var ms = 300;
			timer = setTimeout(function(){
				$.post("/search/", { "scope": "self",
				  "query": value,
				  "csrfmiddlewaretoken" : token }, function(data){
					search_results[value] = data;
					handle_search(data);
				})
			}, ms);
		}
		else
		{
			handle_search(search_results[value]);
		}

	})
});