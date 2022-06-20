odoo.define('de_timesheet_portal', function (require) {
'use strict';
    $(document).ready(function () {
        $('a#timelog_edit').click(function(){
            var id = $(this).attr("data-id");
            var arr = $(this).attr("data-id").split(',');
            var project_id = $(this).attr("data-project-id");
            var task_id = $(this).attr("data-task-id");
           
            
            $("#timelog_edit_modal #id").val(arr[0]);
            $("#timelog_edit_modal #project").val(arr[1]);
            $("#timelog_edit_modal #task").val(arr[2]);
            $("#timelog_edit_modal #project").attr("selected",arr[1])

        })
    })
    var model = 'project.task';
    // Use an empty array to search for all the records
    var domain = [];
    // Use an empty array to read all the fields of the records
    var fields = [];
    rpc.query({
        model: model,
        method: 'search_read',
        args: [domain, fields],
    }).then(function (data) {
        console.log(data);
    });
});
