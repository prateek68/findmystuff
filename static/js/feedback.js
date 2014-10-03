$(document).ready(function(){
  $(".feedback-button").click(function(){
    var url = "{% url 'feedback' %}";
    $("#base-confirmation-modal").load(url, function(){
      $("#base-confirmation-modal").modal('show');
    });
  });
});