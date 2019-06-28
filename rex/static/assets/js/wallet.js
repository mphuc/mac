$(function() {
    $('.button--deposit').on('click',function(){
        var coin = $(this).data('coin');
        $.ajax({
            url: "/account/get-new-address",
            data: {
                type: coin
            },
            type: "POST",
            beforeSend: function() {
                $('.content-show-'+coin).show(300);
                $('.content-all-'+coin).html('<img src="/static/img/ajax-loader.gif" width="120">');
            },
            error: function(data) {
                
            },
            success: function(data) {
                var data = $.parseJSON(data);
                var html = '<div class="form-group text-center"><img style="max-width:300px;" class="address-new-img" alt="" src="https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=bitcoin:'+data.address+'?amount=0"></div><span style="color: #000;" class="address-new">'+data.address+'</span>'
                $('.content-all-'+coin).html(html);
                
            }
        });
        
    })


  $('#input_user_id').on('input propertychange',function(){
    var id_user = $('#input_user_id').val();
    $.ajax({
        url: "/account/get-username-buy-id",
        data: {
            id_user: id_user
        },
        type: "POST",
        beforeSend: function() {
            $('#input_user_name').attr('placeholder','Loading...');
        },
        error: function(data) {
            
        },
        success: function(data) {
          var data = $.parseJSON(data);
          if (data.username == '')
          {
            $('#input_user_name').attr('placeholder','Account does not exist');
          }
          else
          {
            $('#input_user_name').val(data.username);
          }
          
          
        }
    });
  })

    
})



