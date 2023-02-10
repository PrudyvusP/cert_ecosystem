$('#methods_checkbox').on('click', function ()
    {
        if ( $(this).prop('checked') === true )
            {
                $("[name='method_docs']").prop('checked', true);
            }
        else
            {
                $("[name='method_docs']").prop('checked', false);
            }
    }
)