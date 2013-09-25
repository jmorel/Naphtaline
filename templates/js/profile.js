$(document).ready(function() {
    
    $("img#edit_mail").live('click', function() {
        var row = $(this).parent().parent();
        row.children(".content").slideUp('fast');
        row.children("form").fadeIn('fast');
    });
    
    $("form.edit_mail").live('submit', function() {
        var row = $(this).parent()
        var data = {project: $(".misc > #projectWebName").text(),
                    mail: row.children("form").children("input#mail").val()};
        row.children("form").slideUp('fast');
        row.children(".loading").fadeIn('fast');
        $.ajax({
            type: 'POST',
            url: '/updateEMail',
            data: data,
            dataType: 'text',
            error: function() {
                row.children(".loading").slideUp('fast');
                row.children(".error").fadeIn('fast').pause(5000).slideUp('fast', function() {
                row.children(".content").fadeIn('fast');
                });
            },
            success: function(res) {
                if(res == 'ok') {
                    row.children(".loading").slideUp('fast');
                    row.children(".success").fadeIn('fast').pause(5000).slideUp('fast', function() {
                    row.children(".content").children("#content_mail").text(data.mail);
                    row.children(".content").fadeIn('fast');
                    });
                } else {
                    row.children(".loading").slideUp('fast');
                    row.children(".error").fadeIn('fast').pause(5000).slideUp('fast', function() {
                    row.children(".content").fadeIn('fast');
                    });
                }
            }
        });
        return false;
    });
    
    $("img#edit_pwd").live('click', function() {
        var row = $(this).parent().parent();
        row.children(".content").slideUp('fast');
        row.children("form").fadeIn('fast');
    });
    
    $("form.edit_pwd").live('submit', function() {
        var row = $(this).parent()
        var data = {project: $(".misc > #projectWebName").text(),
                    pwd1: row.children("form").children(".pwd1").children("input#pwd1").val(),
                    pwd2: row.children("form").children(".pwd2").children("input#pwd2").val()};
        if( data.pwd1 == data.pwd2) {
            row.children("form").slideUp('fast');
            row.children(".loading").fadeIn('fast');
            $.ajax({
                type: 'POST',
                url: '/updatePwd',
                data: data,
                dataType: 'text',
                error: function() {
                    row.children(".loading").slideUp('fast');
                    row.children(".error").fadeIn('fast').pause(5000).slideUp('fast', function() {
                    row.children(".content").fadeIn('fast');
                    });
                },
                success: function(res) {
                    if(res == 'ok') {
                        row.children(".loading").slideUp('fast');
                        row.children(".success").fadeIn('fast').pause(5000).slideUp('fast', function() {
                        row.children(".content").fadeIn('fast');
                        });
                    } else {
                        row.children(".loading").slideUp('fast');
                        row.children(".error").fadeIn('fast').pause(5000).slideUp('fast', function() {
                        row.children(".content").fadeIn('fast');
                        });
                    }
                }
            }); 
        } else {
            alert(row.children(".error_pwd").text());
        }
        return false;
    });
    
});