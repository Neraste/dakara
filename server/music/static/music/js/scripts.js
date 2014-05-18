function cloneMore(element, type) {
    var newElement = element.clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input:not([type=button])').each(function() {
        var name = $(this).attr('name').replace(/-\d+-/,'-' +  total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    $(".errorlist", newElement).remove();
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace(/-\d+-/,'-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    element.after(newElement);
}

