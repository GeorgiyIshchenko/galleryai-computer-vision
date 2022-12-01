$(document).ready(function () {

    $("#search_input").keyup(function(){
        $("#search_input").css("background-color", "pink");
      $.ajax({
            url: "",
            type: "get",
            data: {
                text: $('#search_input').val()
            },
          success: function (response){

          }
      });

    });

});