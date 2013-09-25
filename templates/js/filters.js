$(document).ready(function(){
	
	var filters_severity = {
		critical : true,
		serious : true,
		light : true
	};
	var filters_status = {
		corrected : true,
		beingtakencareof : true,
		unknown : true
	};
	
	var COOKIE_NAME = 'naphtaline_legend_status';
	var options = { path: '/', expires: 10 };
	
	// read and apply legend status
	var legend_status = $.cookie(COOKIE_NAME);
	if(legend_status == 'up') {
		$("#hide_button").hide();
		$("#show_button").show();
		if($(".selected_tab").attr('id') == "legend_tab") {
			$("#legend_content").hide();
		} else {
			$("#filters_content").hide();
		}
	}
	
	function apply_filters() {
		/*
		// hide/show tickets depending on severity
		if(filters_severity.critical == true) { $(".ticket[ticketSeverity='3'], .updatedTicket[ticketSeverity='3']").show() } 
		else { $(".ticket[ticketSeverity='3'], .updatedTicket[ticketSeverity='3']").hide()}
		if(filters_severity.serious == true) { $(".ticket[ticketSeverity='2'], .updatedTicket[ticketSeverity='2']").show() } 
		else {$(".ticket[ticketSeverity='2'], .updatedTicket[ticketSeverity='2']").hide()}
		if(filters_severity.light == true) { $(".ticket[ticketSeverity='1'], .updatedTicket[ticketSeverity='1']").show() } 
		else {$(".ticket[ticketSeverity='1'], .updatedTicket[ticketSeverity='1']").hide()}
		// hide/show tickets depending on status
		if(filters_status.corrected == true) { $(".ticket[ticketStatus=3]").show() } else {$(".ticket[ticketStatus=3]").hide()}
		if(filters_status.beingtakencareof == true) { $(".ticket[ticketStatus=2]").show() } else {$(".ticket[ticketStatus=2]").hide()}
		if(filters_status.unknown == true) { $(".ticket[ticketStatus=1]").show() } else {$(".ticket[ticketStatus=1]").hide()}
		*/
		
		
		// update display of buttons
		if(filters_severity.critical == true) { $("#filter_severity_critical").removeClass('filter_option').addClass('selected_filter_option') } 
		else { $("#filter_severity_critical").removeClass('selected_filter_option').addClass('filter_option') }
		if(filters_severity.serious == true) {$("#filter_severity_serious").removeClass('filter_option').addClass('selected_filter_option') } 
		else {$("#filter_severity_serious").removeClass('selected_filter_option').addClass('filter_option') }
		if(filters_severity.light == true) {$("#filter_severity_light").removeClass('filter_option').addClass('selected_filter_option') } 
		else {$("#filter_severity_light").removeClass('selected_filter_option').addClass('filter_option') }
		
		if(filters_status.corrected == true) { $("#filter_status_corrected").removeClass('filter_option').addClass('selected_filter_option') } 
		else { $("#filter_status_corrected").removeClass('selected_filter_option').addClass('filter_option') }
		if(filters_status.beingtakencareof == true) { $("#filter_status_beingtakencareof").removeClass('filter_option').addClass('selected_filter_option') } 
		else { $("#filter_status_beingtakencareof").removeClass('selected_filter_option').addClass('filter_option') }
		if(filters_status.unknown == true) {$("#filter_status_unknown").removeClass('filter_option').addClass('selected_filter_option') } 
		else {$("#filter_status_unknown").removeClass('selected_filter_option').addClass('filter_option') }
		
		
	};
	
	// filters need to be applied when page is loaded
	// TODO: load previous state of filters from cookie
	apply_filters();
	
	
	// Behaviour of the filters when one of the switch is pressed
	$("#filter_status_corrected").click(function() {
		filters_status.corrected = !filters_status.corrected;
		apply_filters();
	});
	$("#filter_status_beingtakencareof").click(function() {
		filters_status.beingtakencareof = !filters_status.beingtakencareof;
		apply_filters();
	});
	$("#filter_status_unknown").click(function() {
   		filters_status.unknown = !filters_status.unknown;
		apply_filters();
	});
	$("#filter_severity_critical").click(function() {
		filters_severity.critical = !filters_severity.critical;
		apply_filters();
	});
	$("#filter_severity_serious").click(function() {
		filters_severity.serious = !filters_severity.serious;
		apply_filters();
	});
	$("#filter_severity_light").click(function() {
   		filters_severity.light = !filters_severity.light;
		apply_filters();
	});


	// Tabs management
	// what to do when the "legend" tab is pressed
	$("#legend_tab").click(function() {
		$("#legend_tab").removeClass();
		$("#legend_tab").addClass("selected_tab");
		$("#filters_tab").removeClass();
		$("#filters_tab").addClass("tab");
		if($("#legend_content").css('display') == "none" && $("#filters_content").css('display') == "none") {
			$("#legend_content").slideDown('fast');
			$("#hide_button").show();
			$("#show_button").hide();
			$.cookie(COOKIE_NAME, 'down', options);
		} else if($("#legend_content").css('display') == "block") {
			$("#legend_content").slideUp('fast');
			$("#hide_button").hide();
			$("#show_button").show();
			$.cookie(COOKIE_NAME, 'up', options);
		} else {
			$("#legend_content").show();
			$.cookie(COOKIE_NAME, 'down', options);
		}
		$("#filters_content").hide();
	});
	// what to do when the "filters" tab is pressed
	$("#filters_tab").click(function() {
		$("#filters_tab").removeClass();
		$("#filters_tab").addClass("selected_tab");
		$("#legend_tab").removeClass();
		$("#legend_tab").addClass("tab");
		if($("#legend_content").css('display') == "none" && $("#filters_content").css('display') == "none") {
			$("#filters_content").slideDown('fast');
			$("#hide_button").show();
			$("#show_button").hide();
			$.cookie(COOKIE_NAME, 'down', options);
		} else if($("#filters_content").css('display') == "block") {
			$("#filters_content").slideUp('fast');
			$("#hide_button").hide();
			$("#show_button").show();
			$.cookie(COOKIE_NAME, 'up', options);
		} else {
			$("#filters_content").show();
			$.cookie(COOKIE_NAME, 'down', options);
		}
		$("#legend_content").hide();
	});
	// "hide" button is pressed
	$("#hide_button").click(function() {
		$("#hide_button").hide();
		$("#show_button").show();
		if($(".selected_tab").attr('id') == "legend_tab") {
			$("#legend_content").slideUp('fast');
		} else {
			$("#filters_content").slideUp('fast');
		}
		// update cookie
		$.cookie(COOKIE_NAME, 'up', options);
	});
	// "show" button is pressed
	$("#show_button").click(function() {
		$("#hide_button").show();
		$("#show_button").hide();
		if($(".selected_tab").attr('id') == "legend_tab") {
			$("#legend_content").slideDown('fast');
		} else {
			$("#filters_content").slideDown('fast');
		}
		// update cookie
		$.cookie(COOKIE_NAME, 'down', options);
	});
});

