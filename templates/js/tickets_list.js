$(document).ready(function(){
    
    var solved = $(".misc > #solved").text();
    
    function load_tickets(project, category, solved, selectedTicketRelativeID) {
        var data = {
            project: project,
            category: category,
            solved: solved,
            selectedTicketRelativeID: selectedTicketRelativeID
        };
        $.ajax({
            type:   'POST',
            url:    '/getTicketsList',
            data:   data,
            dataType: 'html',
            error: function() {
                       $("#tickets_loading").hide();
                       $("#tickets_loading_Error").fadeIn('fast');
                   },
            success: function(data) {
                          $("#tickets_loading").hide();
                          $("#tickets_list").html('<div class="dummy"></div>'+data);
                          $("#tickets_list").fadeIn('fast');
                     }
        });
    }
    
    function reloadTickets() {
        //$("#tickets_list").slideUp('fast');
    	//$("#tickets_loading").fadeIn('fast');
        var project = $(".misc > #projectWebName").text();
    	var category = $(".misc > #category").text();
    	var selectedTicketRelativeID = $(".misc > #selectedTicketRelativeID").text() || 0;
        load_tickets(project, category, solved, selectedTicketRelativeID)
    }

    $("#bugs_tab").click(function() {
        // update tab status
    	$("#bugs_tab").removeClass();
    	$("#corrected_bugs_tab").removeClass();
    	$("#bugs_tab").addClass("selected_tab");
    	$("#corrected_bugs_tab").addClass("tab");
    	// display "loading" status
    	$("#tickets_list").hide();
    	$("#tickets_loading").fadeIn('fast');
    	// load tickets
    	var project = $(".misc > #projectWebName").text();
    	var category = $(".misc > #category").text();
    	var selectedTicketRelativeID = $(".misc > #selectedTicketRelativeID").text() || 0;
    	solved = false;
    	load_tickets(project, category, false, selectedTicketRelativeID);
	});
	
    $("#corrected_bugs_tab").click(function() {
        // update tab status
    	$("#bugs_tab").removeClass();
    	$("#corrected_bugs_tab").removeClass();
    	$("#bugs_tab").addClass("tab");
    	$("#corrected_bugs_tab").addClass("selected_tab");
    	// display "loading" status
    	$("#tickets_list").hide();
    	$("#tickets_loading").fadeIn('fast');
    	// load tickets
    	var project = $(".misc > #projectWebName").text();
    	var category = $(".misc > #category").text();
    	var selectedTicketRelativeID = $(".misc > #selectedTicketRelativeID").text() || 0;
    	solved = true;
    	load_tickets(project, category, true, selectedTicketRelativeID);
    });
    

    // SORTING
    $("div.sort_controllers > .ticket_id_list").live('click', function() {
        var mode='idDown';
        if($("div.sort_controllers > .ticket_id_list > img").attr('alt') == 'triangle down') {
            mode = 'idUp';
        }
        var data = {project: $(".misc > #projectWebName").text(),
                    mode: mode};
        $.ajax({
            type: 'POST',
            url: '/setSort',
            data: data,
            dataType: 'text',
            success: reloadTickets
        });
    });
    $("div.sort_controllers > .ticket_status_list").live('click', function() {
        var mode='statusDown';
        if($("div.sort_controllers > .ticket_status_list > img").attr('alt') == 'triangle down') {
            mode = 'statusUp';
        }
        var data = {project: $(".misc > #projectWebName").text(),
                    mode: mode};
        $.ajax({
            type: 'POST',
            url: '/setSort',
            data: data,
            dataType: 'text',
            success: reloadTickets
        });
    });
    $("div.sort_controllers > .ticket_severity_list").live('click', function() {
        var mode='severityDown';
        if($("div.sort_controllers > .ticket_severity_list > img").attr('alt') == 'triangle down') {
            mode = 'severityUp';
        }
        var data = {project: $(".misc > #projectWebName").text(),
                    mode: mode};
        $.ajax({
            type: 'POST',
            url: '/setSort',
            data: data,
            dataType: 'text',
            success: reloadTickets
        });
    });
    $("div.sort_controllers > .ticket_title_list").live('click', function() {
        var mode='lastModDown';
        if($("div.sort_controllers > .ticket_title_list > img").attr('alt') == 'triangle down') {
            mode = 'lastModUp';
        }
        var data = {project: $(".misc > #projectWebName").text(),
                    mode: mode};
        $.ajax({
            type: 'POST',
            url: '/setSort',
            data: data,
            dataType: 'text',
            success: reloadTickets
        });        
    });
    
});