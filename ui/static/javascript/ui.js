$(document).ready(function() {
  $("#submitButton").click(function(){
    var article = $("#inputArticle").val();
    $("#outputArticle").val("");
    $.ajax({
      url: '/word_segment',
      data: {
        article: article
      },
      type: 'GET',
      success: function(response) {
        $("#outputArticle").val(response.article);
      },
      error: function(error) {
        console.log(error);
      }
    });
  })
});
