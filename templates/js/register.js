$(document).ready(function() {
    
    $("form.register").live('submit', function(e) {
	$(".error").slideUp('fast');
        // collect data
        var data = {projectWebName: $("#projectWebName").text(),
                    login: $("#login").val(),
                    pwd1: $("#pwd1").val(),
                    pwd2: $("#pwd2").val(),
                    email: $("#email").val()};
        // check data
        var ok = true;
        if(data.pwd1 != data.pwd2) {
            $("#pwd_bis_error").fadeIn('fast');
            ok = false;
        }
        if(data.pwd1 == '' || data.pwd2 == '') {
            $("#pwd_error").fadeIn('fast');
            ok = false;
        }
        if(data.login == '') {
            $("#login_empty").fadeIn('fast');
            ok = false;            
        }
        if(data.email == '') {
            $("#email_empty").fadeIn('fast');
            ok = false;            
        }
        
        // no errors found
        if(ok) {
            // display loading 
            $("form.register").slideUp('fast');
            $("div.loading").fadeIn('fast');        
            // process request
            $.ajax({
                type: 'POST',
                url: '/doRegister',
                data: data,
                dataType: 'json',
                error: function(a, b, c) {
                    $("div.loading").slideUp('fast');
                    $("div.error_connect").fadeIn('fast').pause(5000).slideUp('fast', function() {
                    $("form.register").fadeIn('fast');
                    }); 
                },
                success: function(res) {
                    // check result
                    var ok = true;
                    if(!res.equalPwd) {
                        $("#pwd_bis_error").fadeIn('fast');
                        ok = false;
                    }
                    if(res.emptyPwd) {
                        $("#pwd_error").fadeIn('fast');
                        ok = false;
                    }
                    if(res.emptyLogin) {
                        $("#login_empty").fadeIn('fast');
                        ok = false;            
                    }
                    if(res.emptyEMail) {
                        $("#email_empty").fadeIn('fast');
                        ok = false;            
                    }
                    if(res.loginTaken) {
                    	$("#login_taken").fadeIn('fast');
                    	ok = false;
                    }
                    if(ok) {
                    	if(res.ok) {
                    		$("div.loading").slideUp('fast');
                    		$("div.success").fadeIn('fast');
                    	}
                    } else {
                        $("div.loading").slideUp('fast');
                        $("form.register").fadeIn('fast');
                    }
                    
                }
            });
        }
	return false;
	//e.preventDefault();
    });

});
