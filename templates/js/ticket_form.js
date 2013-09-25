function bindUploadFileForTicket() {
    n = 0;
    if($("span#add_file").size() > 0) {
        new AjaxUpload('add_file', {
            action: '/addFile',
            name: 'file',
            data: {project: $("input[type='hidden'][name='project']").val(),
                   file_type: 'ticket'},
            autoSubmit: true,
            onChange: function(file, extension) {
                    this.name = file;
                    n = n+1;   
                    $(".add_files").append(
                    '<div class="file" id="'+n+'">'
                    +'  <div class="file_message" id="deleting"><img src="/pix/loading_wheel.gif" alt="loading wheel" /> Deleting file, please wait.</div>'
                    +'  <div class="file_message" id="deleting_error">The file could not be deleted.</div>'
                    +'  <div class="file_message" id="deleting_success">The file was deleted with success.</div>'
                    +'  <div class="file_message" id="loading_file"><img src="/pix/loading_wheel.gif" alt="loading wheel" /> Uploading file, please wait.</div>'
                    +'  <div class="file_message" id="loading_error">An error occurred during the upload of '+file+'.</div>'
                    +'  <div class="file_data">'
                    +'      <span class="remove_existing" id="TODO"><img src="/pix/red_cross.png" alt="remove this file button" /></span>'+file
                    +'      <input type="hidden" name="hidden_file" />'
                    +'  </div>'
                    +'</div>');
                    var f = $(".file[id='"+n+"']");
                    f.children(".file_data").hide();
                    f.children("#loading_file").fadeIn('fast');
                },
            onComplete: function(file, response) {
                    // if everything went well, response should be a string like: "ok:1234" where 1234 is the file id in the database
                    var status = response.substr(0, 2);
                    var id = response.substr(3);
                    var f = $(".file[id='"+n+"']");
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
}



$(document).ready(function() {

    // FILE MANAGEMENT
    // adding and removing file    
    bindUploadFileForTicket();
    
    // deleting already uploaded files
    $(".remove_existing").live('click',function() {
        // display loading wheel
        var file = $(this).parent().parent();
        file.children(".file_data").hide();
        file.children("#deleting").fadeIn('fast');
        id = $(this).attr('id');
        var data = {project: $("input[type='hidden'][name='project']").val(),
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
    
    // CREATE TICKET
    function create_ticket() {
        // collecting data from the form
        files = Array();
        $("input[name='hidden_file']").each(function() {
            files.push($(this).attr('id'));
        });
        data = {project: $(".misc > #projectWebName").text(),
                category:  $(".misc > #category").text(),
                relativeID: $(".misc > #selectedTicketRelativeID").text(),
                status: '',
                severity: '',
                name: '',
                description: '',
                files: files};
        var fields = $(":input").serializeArray();
        var mode = 'edit';
        jQuery.each(fields, function(i, field){
            if(field.name in data) {
                data[field.name] = field.value;
            }
            if(field.name=='mode') {
                mode = field.value;
            }
        });
        
        if(mode == 'edit') {
            var destination = '/editTicket';
        } else if(mode == 'new') {
            var destination = '/saveTicket';
        } else {
            location.href = '/'+data.project;
        }
        
        // initiate request
       $.ajax({
            type:   'POST',
            url:    destination,
            data:   data,
            dataType: 'json',
            error:  function(XMLHttpRequest, textStatus, errorThrown) {
                        $("div.loading").slideUp('fast'); 
                        $("div.error").fadeIn('fast'); // display error message
                        $("div.error").append('<br/>Data: '+XMLHttpRequest);
                        $("div.error").append('<br/>TextStatus: '+textStatus);
                        $("div.error").append('<br/>errorThrown: '+errorThrown);
                    },
            success: function(res, text_status) {
                        $("div.loading").slideUp('fast');
                        var url = '/'+data.project+'/'+data.category+'/'+res.relativeID;    
                        $("div.thanks").children('a#redirecturl').attr('href', url);
                        $("div.thanks").fadeIn('fast');  // display thanks message
                        location.href = url;
                     }
            
        });
    }
    
    // what should we do when "ok" button is pressed ?
    $("form.create").live('submit', function() {
        // display "loading message"
        $("form.create").slideUp('fast');
        $("div.loading").fadeIn('fast');
        create_ticket();
        return false;
    });
    $("#tryagain").live('click', function() {
        $("div.error").slideUp('fast');
        $("div.loading").fadeIn('fast');
        create_ticket();
    });
    
});