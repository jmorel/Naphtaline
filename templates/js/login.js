$(document).ready(function() {
	
	$("#login").focus();
	
	if($("#login").attr("value") == '') {
		$("#login").attr("value", "login");
	}
	if($("#password").attr("value") == '') {
		$("#password").attr("value", "password");
	}
	
	$("#login").click(function() {
		if($("#login").attr("value") == 'login') {
			$("#login").attr("value", '');
		}
	});
	$("#password").click(function() {
		if($("#password").attr("value") == 'password') {
			$("#password").attr("value", '');
		}
	});
	
	function login() {
	   $("form").slideUp('fast');
	   $(".loading").fadeIn('fast');
	   
	   data = {project: $(".misc > #projectWebName").text(),
	           login: $("#login").val(),
	           password: $("#password").val()};
	           
	   $.ajax({
	       url: '/doLogin',
	       type: 'POST',
	       data: data,
	       dataType: 'text',
	       error: function() {
	           $(".loading").slideUp('fast');
	           $(".error").fadeIn('fast');
	       },
	       success: function(res) {
	           if(res=='ok') {
	               location.href = $(".misc > #comingFrom").text();
	           } else {
	               $(".loading").slideUp('fast');
	               $(".wrong").fadeIn('fast');
	               $("form").fadeIn('fast');
	           }
	       }
	   });
	   return false;
	}
	
	$("form").submit(login);
	$("span#retry").click(login);
	
});