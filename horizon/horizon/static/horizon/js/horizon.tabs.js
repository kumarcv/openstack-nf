horizon.tabs = {};

horizon.tabs.load_tab = function (evt) {
  var $this = $(this),
      tab_id = $this.attr('data-target'),
      tab_pane = $(tab_id);

  // FIXME(gabriel): This style mucking shouldn't be in the javascript.
  tab_pane.append("<span style='margin-left: 30px;'>" + gettext("Loading") + "&hellip;</span>");
  tab_pane.spin(horizon.conf.spinner_options.inline);
  $(tab_pane.data().spinner.el).css('top', '9px');
  $(tab_pane.data().spinner.el).css('left', '15px');

  // If query params exist, append tab id.
  if(window.location.search.length > 0) {
    tab_pane.load(window.location.search + "&tab=" + tab_id.replace('#', ''));
  } else {
    tab_pane.load("?tab=" + tab_id.replace('#', ''));
  }
  $this.attr("data-loaded", "true");
  evt.preventDefault();
};

horizon.addInitFunction(function () {
  var data = horizon.cookies.read('tabs');

  $(".tab-content").find(".js-tab-pane").addClass("tab-pane");
  horizon.modals.addModalInitFunction(function (el) {
    $(el).find(".js-tab-pane").addClass("tab-pane");
  });

  $(document).on("show", ".ajax-tabs a[data-loaded='false']", horizon.tabs.load_tab);

  $(document).on("shown", ".nav-tabs a[data-toggle='tab']", function (evt) {
    var $tab = $(evt.target),
        $content = $($(evt.target).attr('data-target'));
    horizon.datatables.update_footer_count($content.find("table"));
    horizon.cookies.update("tabs", $tab.closest(".nav-tabs").attr("id"), $tab.attr('data-target'));
  });

  // Initialize stored tab state for tab groups on this page.
  $(".nav-tabs[data-sticky-tabs='sticky']").each(function (index, item) {
    var $this = $(this),
        id = $this.attr("id"),
        active_tab = data[id];
    // Set the tab from memory if we have a "sticky" tab and the tab wasn't explicitly requested via GET.
    if (active_tab && window.location.search.indexOf("tab=") < 0) {
      $this.find("a[data-target='" + active_tab + "']").tab('show');
    }
  });

  // Enable keyboard navigation between tabs in a form.
  $(document).on("keydown", ".tab-pane :input:visible:last", function (evt) {
    var $this = $(this),
        next_pane = $this.closest(".tab-pane").next(".tab-pane");
      // Capture the forward-tab keypress if we have a next tab to go to.
      if (evt.which === 9 && !event.shiftKey && next_pane.length) {
        evt.preventDefault();
        $(".nav-tabs a[data-target='#" + next_pane.attr("id") + "']").tab('show');
      }
  });
  $(document).on("keydown", ".tab-pane :input:visible:first", function (evt) {
    var $this = $(this),
        prev_pane = $this.closest(".tab-pane").prev(".tab-pane");
      // Capture the forward-tab keypress if we have a next tab to go to.
      if (event.shiftKey && evt.which === 9 && prev_pane.length) {
        evt.preventDefault();
        $(".nav-tabs a[data-target='#" + prev_pane.attr("id") + "']").tab('show');
        prev_pane.find(":input:last").focus();
        console.log(prev_pane);
      }
  });

  $(document).on("focus", ".tab-content :input", function () {
    var $this = $(this),
        tab_pane = $this.closest(".tab-pane"),
        tab_id = tab_pane.attr('id');
    if (!tab_pane.hasClass("active")) {
      $(".nav-tabs a[data-target='#" + tab_id + "']").tab('show');
    }
  });
});
