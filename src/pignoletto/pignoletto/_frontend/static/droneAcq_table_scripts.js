var minDate, maxDate;
    // Custom filtering function which will search data in column four between two values
    $.fn.dataTable.ext.search.push(
        function(settings, data, dataIndex) {
            var min = minDate.val();
            var max = maxDate.val();
            var date = new Date(data[3]);
    
            if (
                (min === null && max === null) ||
                (min === null && date <= max) ||
                (min <= date && max === null) ||
                (min <= date && date <= max)
            ) {
                return true;
            }
            return false;
        }
    );
    $(document).ready(function () {
        // Create date inputs
        minDate = new DateTime($('#min'), {
            format: 'MMMM Do YYYY'
        });
        maxDate = new DateTime($('#max'), {
            format: 'MMMM Do YYYY'
        });

        let keys = [];
        $.ajax({
            url: "/pignoletto/get_drone_acq_keys",
            type: 'GET',
            dataType: 'JSON',
            async: false,
            success: function(data) {
            keys = data;
            } 
        });
  
        let col = keys.map(test);
        function test(value) {
            return {data: value, orderable: (value=="sito" || value=="time" || value=="start_acq_time" || value=="stop_acq_time")?true:false};
        }

        var table = $('#data').DataTable({
            ajax: "/pignoletto/get_drone_acquisitions",
            serverSide: false,
            columns: col,
            scrollY: '65vh',
            scrollX: true,
            scrollCollapse: true,
            deferRender: true,
            dom: 'Blrtip',  // Blfrtip -> to show the general filter tab
            buttons: [
                {
                    extend: 'csv',
                    text: 'Download data as CSV',
                    filename: 'Drone_acquisitions'
                }
            ]
        });

        // Refilter the table
        $('#min, #max').on('change', function() {
            table.draw();
        });

        // Apply the search
        table.columns().each(function(colIdx) {
            $('input#sito').on('keyup change clear', function() {
                table
                    .column(':contains(sito)')
                    .search(this.value)
                    .draw();
            } );
        } );

        // Modify download button
        $('button.dt-button').css({"background": "none", "border": "none"});
        $('button.dt-button>span').prepend('<img src="./static/download1.png" alt="Download csv"/>');
        $('div.dt-buttons').css({"display": "flex", "justify-content": "center"});

    });