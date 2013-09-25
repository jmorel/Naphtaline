$(document).ready(function() {
    
    $("form.lost_pwd").live('submit', function() {
        $(".error").slideUp('fast');
        // collect data
        var data = {projectWebName: $("#projectWebName").text(),
                    login: $("#login").val()};
        // check data
        var ok = true;
        if(data.login == '') {
            $("#login_empty").fadeIn('fast');
            ok = false;            
        }
        
        // no errors found
        if(ok) {
            // display loading 
            $("form.lost_pwd").slideUp('fast');
            $("div.loading").fadeIn('fast');        
            // process request
            $.ajax({
                type: 'POST',
                url: '/doLostPassword',
                data: data,
                dataType: 'text',
                error: function(a, b, c) {
                    $("div.loading").slideUp('fast');
                    $("div.error_connect").fadeIn('fast').pause(5000).slideUp('fast', function() {
                    $("form.lost_pwd").fadeIn('fast');
                    }); 
                },
                success: function(res) {
                    // check result
                    if(res == 'not found') {
			$("div.loading").slideUp('fast');
			$("form.lost_pwd").fadeIn('fast');
			$("#login_not_found").fadeIn('fast');
		    } else if(res == 'ok'){
			$("div.loading").slideUp('fast');
                    	$("div.success").fadeIn('fast');
		    } else {
			$("div.loading").slideUp('fast');
			$("div.error_connect").fadeIn('fast').pause(5000).slideUp('fast', function() {
			$("form.lost_pwd").fadeIn('fast');
			}); 
		    }
                }
            });
        }
	return false;
    });

});