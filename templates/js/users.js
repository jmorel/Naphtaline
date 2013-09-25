$(document).ready(function() {
    
    function delete_user(user) {
        
        user.children("div").slideUp('fast');
        user.children(".loading").fadeIn('fast');
        data = {project: $(".misc > #projectWebName").text(),
                userID: user.attr('id')};
        $.ajax({
            url: '/deleteUser',
            data: data,
            type: 'POST',
            dataType: 'text',
            error: function() {
                user.children(".loading").slideUp('fast');
                user.children(".error").fadeIn('fast');
                user.children(".error").pause(5000).slideUp('fast', function() {
                user.children(".login, .action, .email, .status").fadeIn('fast');
                });
            },
            success: function(res) {
                if(res == 'ok') {
                    user.children(".loading").slideUp('fast');
                    user.children(".delete_success").fadeIn('fast');
                    user.children(".delete_success").pause(5000).slideUp('fast', function() {
                    user.remove();
                    });
                } else if(res == 'owner') {
                    user.children(".loading").slideUp('fast');
                    user.children(".error_owner").fadeIn('fast');
                    user.children(".error_owner").pause(5000).slideUp('fast', function() {
                    user.children(".login, .action, .email, .status").fadeIn('fast');
                    });
                } else {
                    user.children(".loading").slideUp('fast');
                    user.children(".error").fadeIn('fast');
                    user.children(".error").pause(5000).slideUp('fast', function() {
                    user.children(".login, .action, .email, .status").fadeIn('fast');
                    });
                }
            }
        });
    }
    
    function accept_user(user) {
        user.children("div").slideUp('fast');
        user.children(".loading").fadeIn('fast');
        data = {project: $(".misc > #projectWebName").text(),
                userID: user.attr('id'),
                level: user.children("div.status").children("select").children("option:selected").val()};
        $.ajax({
            url: '/acceptUser',
            data: data,
            type: 'POST',
            dataType: 'text',            
            error: function() {
                user.children(".loading").slideUp('fast');
                user.children(".error").fadeIn('fast');
                user.children(".error").pause(5000).slideUp('fast', function() {
                user.children(".login, .action, .email, .status").fadeIn('fast');
                });
            },
            success: function(res) {
                user.children(".loading").slideUp('fast');
                user.children(".accept_success").fadeIn('fast');
                user.children(".accept_success").pause(3000).slideUp('fast', function() {
                // take the existing div and move it to the "users" list
                // this requires some modifications
                user.children("div.action#accept").remove();
                user.children("div.action").removeClass("action").addClass("delete");
                user.children("div.delete").children("img").attr("src", '/pix/delete.png');
                user.removeClass("subscription_request").addClass("registered_user");
                $("div.section#users").append(user);
                user.children(".login, .delete, .email, .status").fadeIn('fast');
                });
            }
        });
    }
    
    function change_level(user) {
        user.children("div").slideUp('fast');
        user.children(".loading").fadeIn('fast');
        data = {project: $(".misc > #projectWebName").text(),
                userID: user.attr('id'),
                level: user.children("div.status").children("select").children("option:selected").val()};
        $.ajax({
            url: '/updateUserLevel',
            data: data,
            type: 'POST',
            dataType: 'text',            
            error: function() {
                user.children(".loading").slideUp('fast');
                user.children(".error").fadeIn('fast');
                user.children(".error").pause(5000).slideUp('fast', function() {
                user.children(".login, .delete, .email, .status").fadeIn('fast');
                });
            },
            success: function(res) {
                if(res == 'ok') {
                    user.children(".loading").slideUp('fast');
                    user.children(".update_success").fadeIn('fast');
                    user.children(".update_success").pause(3000).slideUp('fast', function() {
                    user.children(".login, .delete, .email, .status").fadeIn('fast');
                    });
                } else {
                    user.children(".loading").slideUp('fast');
                    user.children(".error").fadeIn('fast');
                    user.children(".error").pause(5000).slideUp('fast', function() {
                    user.children(".login, .delete, .email, .status").fadeIn('fast');
                });
                }
            }
        });
    }
    
    function send_invitations(section) {
        
        section.children(".info").slideUp('fast');
        section.children("form").slideUp('fast');
        section.children(".loading").fadeIn('fast');
        
        var data = {project: $(".misc > #projectWebName").text(),
                    to: $("textarea[name='to']").val(),
                    msg: $("textarea[name='message']").val()};
        $.ajax({
            type: 'POST',
            url: '/sendInvitations',
            data: data,
            dataType: 'text',            
            error: function() {
                section.children(".loading").slideUp('fast');
                section.children(".error").fadeIn('fast').pause(3000).slideUp('fast', function() {
                section.children(".info").fadeIn('fast');
                section.children("form").fadeIn('fast');
                });
            },
            success: function() {
                section.children(".loading").slideUp('fast');
                section.children(".success").fadeIn('fast').pause(3000).slideUp('fast', function() {
                section.children(".info").fadeIn('fast');
                section.children("form").fadeIn('fast');
                section.children("form").children("div").children("textarea").val('');
                });
            }
        });
    }
    
    // accept request
    $("img#accept").live('click', function() {
        accept_user($(this).parent().parent());
    });
    // reject request
    $("img#reject").live('click', function() {
        var ok = confirm($(".misc > #rejectMsg").text());
        if(ok) {
            return delete_user($(this).parent().parent());
        } else {
            return false;
        } 
    });
    // delete registered user
    $("img#delete").live('click', function() {
        var ok = confirm($(".misc > #deleteMsg").text());
        if(ok) {
            return delete_user($(this).parent().parent());
        } else {
            return false;
        }
    });
    // change registered user's status
    $("select#status").live('change', function() {
        var cat = $(this).parent().parent();
        if(cat.attr('class')=='registered_user') {
            change_level($(this).parent().parent());
        }
    });
    $("form.invitations").live('submit', function() {
        send_invitations($(this).parent());
        return false;
    });
});