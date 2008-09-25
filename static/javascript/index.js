function do_post(action, name_value){
    var form = document.createElement('form');
    form.method='post';
    form.action = action;
    var name_input = document.createElement('input');
    name_input.setAttribute('name', 'name');
    name_input.setAttribute('value', name_value);
    form.appendChild(name_input);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

$(document).ready(function(){
    $('#proglist').children().click(function(){
        window.location = "program/" + $(this).text() + "/";
    });
    $('#add_button').click(function(event){
        event.preventDefault();
        var prog_name = prompt("Enter name of Program to Add");
        if(prog_name){
            do_post("/mips/add/", prog_name);
        }
    });
    $('#del_button').click(function(event){
        event.preventDefault();
        var prog_name = prompt("Enter Name of Program to Delete");
        if(prog_name){
            do_post("/mips/del/", prog_name);
        }
    });
});