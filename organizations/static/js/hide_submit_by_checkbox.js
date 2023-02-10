$('#final_check').on('click', function ()
    {
        if ( $(this).prop('checked') === true )
            {
                $(".btn").attr('disabled', false);
            }
        else
            {
                $(".btn").attr('disabled', true);
            }
    }
)