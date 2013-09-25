$(document).ready(function() {
    
    $("form#new_project").live('submit', function() {
        $(".error").slideUp('fast');
        // collect data
        var data = {projectWebName: $("#projectWebName").val(),
                    projectName: $("#projectName").val(),
                    login: $("#login").val(),
                    pwd1: $("#pwd1").val(),
                    pwd2: $("#pwd2").val(),
                    email: $("#email").val(),
		    lang: $("#lang").val()};
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
        if(data.projectWebName == '') {
            $("#webname_empty").fadeIn('fast');
            ok = false;
        }
        if(data.projectName == '') {
            $("#name_empty").fadeIn('fast');
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
            $("form#new_project").slideUp('fast');
            $("div.loading").fadeIn('fast');        
            // process request
            $.ajax({
                type: 'POST',
                url: '/createProject',
                data: data,
                dataType: 'json',
                error: function(a, b, c) {
                    $("div.loading").slideUp('fast');
                    $("div.error_connect").fadeIn('fast').pause(5000).slideUp('fast', function() {
                    $("form#new_project").fadeIn('fast');
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
                    if(!res.validProjectWebName) {
                        $("#webname_used").fadeIn('fast');
                        ok = false;
                    }
                    if(res.emptyProjectWebName) {
                        $("#webname_chars").fadeIn('fast');
                        ok = false;
                    }
                    if(res.emptyProjectName) {
                        $("#name_empty").fadeIn('fast');
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
                    if(ok) {
                    	if(res.ok) {
                    		$("div.loading").slideUp('fast');
                    		$("div.success").fadeIn('fast', function() {
                    			location.href='http://projects.naphtaline.net/'+data.projectWebName;
                    		});
                    	}
                    } else {
                        $("div.loading").slideUp('fast');
                        $("form#new_project").fadeIn('fast');
                    }
                    
                }
            });
        }
	return false;
    });

});