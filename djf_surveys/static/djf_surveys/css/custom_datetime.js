document.addEventListener("DOMContentLoaded", function () {
    $(function () {
        $('#id_valid_until').datetimepicker({
            format: 'Y-m-d H:i',
            step: 30  // Adjusts time selection intervals
        });
    });
});
