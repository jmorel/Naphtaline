$(document).ready(function() {
    
    $("#edit_button").live('click', function() {
        $(".ticket > div[class!='ticket_type_id']").slideUp('fast');
        $(".ticket > div.edit_loading").fadeIn('fast');
        var data = {
            project: $(".misc > #projectWebName").text(),
            category: $(".misc > #category").text(),
            ticketRelativeID: $(".misc > #selectedTicketRelativeID").text()
        };
        $.ajax({
            type: 'POST',
            url: '/editTicketForm',
            data: data,
            dataType: 'html',
            error: function(a,b,c,d) {},
            success: function(res, text_status) {
                $("div.edit_loading").slideUp('fast');
                $("div.ticket").append(res);
                bindUploadFileForTicket();
            }
        });
        
    });
    
    $("#delete_button").live('click', function() {
        var ok = confirm($("#deleteMsg").text());
        if(ok) {
            var data = {project: $(".misc > #projectWebName").text(),
                        category: $(".misc > #category").text(),
                        ticketID: $(".misc > #selectedTicketRelativeID").text()};
            $(".ticket > div").slideUp('fast');
            $.ajax({
                type: 'POST',
                url: '/deleteTicket',
                dataType: 'text',
                data: data,
                error: function() {
                    $(".delete_loading").slideUp('fast');
                    $(".delete_error").fadeIn('fast');
                },
                success: function(res, textStatus) {
                    if(res == 'ok') {
                        $(".delete_loading").slideUp('fast');
                        $(".delete_success").fadeIn('fast');
                        location.href = '/'+data.project+'/'+data.category;
                    } else {
                        $(".delete_loading").slideUp('fast');
                        $(".delete_error").fadeIn('fast');
                    }
                }
            });
        }
    });
});