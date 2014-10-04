$(document).ready(function(){
  $(".feedback-button").click(function(){
    $("#base-confirmation-modal").load(window.feedback_url, function(){
      $("#base-confirmation-modal").modal('show');
    });
  });
});