function code_view_is_editable(){
    return $('#code_view').attr('readonly') == "";
}
function set_code_view_editable(){
    $('#code_view').attr('readonly', '');
    $('#editable').show();
}
function set_code_view_uneditable(){
    $('#code_view').attr('readonly', 'true');
    $('#editable').hide();
}

$(document).ready(function(){

    Ext.state.Manager.setProvider(new Ext.state.CookieProvider());
    var output = new Ext.Panel({
        width: 200,
        height: 300,
        margins   : '3 3 3 3',
        title    : 'Output',
        html     : ''
    });
    var memory = new Ext.Panel({
        title : 'Memory',
        width : 200,
        height: 300,
        margins : '3 0 3 3',
        cmargins : '3 3 3 3',
        html : ''
    });

    var store = new Ext.data.JsonStore({
        root : 'registers',
        fields: ['name', {name: 'value', type: 'int'}]
    });


    var registers = new Ext.grid.GridPanel({
        store: store,
        ctCls: 'black-text',
        columns: [
            {id:'name', header:'Name', width: 100, sortable: true, dataIndex: 'name'},
            {header: 'Value', width: 100, sortable: true, dataIndex: 'value'}],
        stripeRows: true,
        width: 225,
        height: 300,
        margins: '3 0 3 3',
        title: 'Register Grid'
    });

    var win = new Ext.Window({
        title    : 'Console',
        closable : true,
        closeAction : 'hide',
        autoWidth: true,
        autoHeight: true,
        layout   : 'column',
        items    : [registers, memory, output]
    });

    $('#edit').click(function(event){
        event.preventDefault();
        if(code_view_is_editable()){
            set_code_view_uneditable();
        }
        else{
            set_code_view_editable();
        }
    });
    $('#home').click(function(event){
        event.preventDefault();
        window.location = "/mips/";
    });
    $('#run').click(function(event){
        event.preventDefault();
        var options = {
            url: ('/mips/program/' + program_name + '/run/'),
            success: function(responseText, statusText) {
                data = eval("(" + responseText + ")");
                if(data.exception){
                    alert("Exception : " + data.exception);
                }
                else{
                    lines = data.output
                    for(i = 0; i < lines.length; i++){
                        output.html += lines[i] + "<br />";
                    }
                    store.loadData(data);
                    win.show(Ext.get('run'));
                }
            }
        };
        $('#code_form').ajaxSubmit(options);
    });
    $('#update').click(function(event){
        event.preventDefault();
        $('#code_form').attr('action', "/mips/program/" + program_name + "/update/").submit();
    });
});
