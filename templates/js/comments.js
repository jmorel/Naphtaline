$(document).ready(function() {

    // MANAGE FILES
    // add file
    var n_comment = 0;
    
    function bindUploadScript() {
        new AjaxUpload('add_comment_add_file', {
            action: '/addFile',
            name: 'file',
            data: {project: $(".misc > #projectWebName").text(),
                   file_type: 'comment'},
            autoSubmit: true,
            onChange: function(file, extension) {
                    this.name = file;
                    n_comment = n_comment + 1;   
                    $(".add_comment_files").append(
                    '<div class="add_comment_file" id="'+n_comment+'">'
                    +'  <div class="file_message" id="deleting"><img src="/pix/loading_wheel.gif" alt="loading wheel" /> Deleting file, please wait.</div>'
                    +'  <div class="file_message" id="deleting_error">The file could not be deleted.</div>'
                    +'  <div class="file_message" id="deleting_success">The file was deleted with success.</div>'
                    +'  <div class="file_message" id="loading_file"><img src="/pix/loading_wheel.gif" alt="loading wheel" /> Uploading file, please wait.</div>'
                    +'  <div class="file_message" id="loading_error">An error occurred during the upload of '+file+'.</div>'
                    +'  <div class="file_data">'
                    +'      <span class="remove_existing" id="TODO"><img src="/pix/red_cross.png" alt="remove this file button" /></span>'+file
                    +'      <input type="hidden" name="hidden_comment_file" />'
                    +'  </div>'
                    +'</div>'
                    );
                    var f = $(".add_comment_file[id='"+n_comment+"']");
                    f.children(".file_data").hide();
                    f.children("#loading_file").fadeIn('fast');
                },
            onComplete: function(file, response) {
                    var status = response.substr(0, 2);
                    var id = response.substr(3);
                    var f = $(".add_comment_file[id='"+n_comment+"']");
                    if(status == 'ok') {
                        f.children("#loading_file").hide();
                        f.children(".file_data").fadeIn('fast');
                        f.children(".file_data").children(".remove_existing").attr('id', id);
                        f.children(".file_data").children("input[type='hidden']").attr('id', id);
                    } else {
                        f.children("#loading_file").hide();
                        f.children("#loading_error").fadeIn('fast').pause(5000).fadeOut('fast');
                    }
    
                }   
        });
    }
    
    bindUploadScript();
        
    // remove file
    $(".remove_existing").live('click', function() {
        // display loading wheel
        var file = $(this).parent().parent();
        file.children(".file_data").hide();
        file.children("#deleting").fadeIn('fast');
        id = $(this).attr('id');
        var data = {project: $(".misc > #projectWebName").text(),
                    id: id};
        function delete_error() {
            file.children("#deleting").hide()
            file.children("#deleting_error").fadeIn('fast');
            file.children("#deleting_error").pause(5000).fadeOut('fast', function() {file.children(".file_data").fadeIn('fast');});
        }
        function delete_success() {
            file.children("#deleting").hide()
            file.children("#deleting_success").fadeIn('fast').pause(5000).fadeOut('fast',function() {file.remove();});
        }
        $.ajax({
            type:   'POST',
            url:    '/deleteFile',
            data:   data,
            dataType: 'text',
            error: delete_error,
            success: function(data, text_status) {
                        if(data=='0') {delete_success()}
                        else  {delete_error()}
                     }
            
        });
    });

    // ADD COMMENT
    function reload_comments() {
        var data = {project: $(".misc > #projectWebName").text(),
                    category:  $(".misc > #category").text(),
                    ticketRelativeID: $(".misc > #selectedTicketRelativeID").text()}
        $.ajax({
            type:   'POST',
            url:    '/getCommentsList',
            data:   data,
            dataType: 'html',
            error:  function(XMLHttpRequest, textStatus, errorThrown) {
                        $("div.comments_loading").slideUp('fast'); 
                        $("div.comments_error").fadeIn('fast'); // display error message
                        $("div.comments_error").append('<br/>Data: '+XMLHttpRequest);
                        $("div.comments_error").append('<br/>TextStatus: '+textStatus);
                        $("div.comments_error").append('<br/>errorThrown: '+errorThrown);
                    },
            success: function(data, text_status) {
                        $("div.comments").html(data);
                        bindUploadScript();
                     }
            
        });
    }
       
    function add_comment() {
        // collecting data from the form
        files = Array();
        $("input[name='hidden_comment_file']").each(function() {
            files.push($(this).attr('id'));
        });
        var data = {project: $(".misc > #projectWebName").text(),
                category:  $(".misc > #category").text(),
                relativeID: $(".misc > #selectedTicketRelativeID").text(),
                content: $("#form_comment > textarea").val(),
                files: files};
        // initiate request
       $.ajax({
            type:   'POST',
            url:    '/saveComment',
            data:   data,
            dataType: 'text',
            error:  function(XMLHttpRequest, textStatus, errorThrown) {
                        $("div.comment_loading").slideUp('fast'); 
                        $("div.comment_error").fadeIn('fast'); // display error message
                        $("div.comment_error").append('<br/>Data: '+XMLHttpRequest);
                        $("div.comment_error").append('<br/>TextStatus: '+textStatus);
                        $("div.comment_error").append('<br/>errorThrown: '+errorThrown);
                    },
            success: function(res, text_status) {
                        $("div.comment_loading").slideUp('fast');
                        $("div.comment_thanks").fadeIn('fast');  // display thanks message
                        // using relaod_comments cause issues
                        //reload_comments();
                        location.href = '/'+data.project+'/'+data.category+'/'+data.relativeID
                     }
            
        });
    }
    
    $("input.add_comment_ok").click(function() {
        // display "loading message"
        $("form#form_comment").slideUp('fast');
        $("div.comment_loading").fadeIn('fast');
        add_comment();         
    });
});