function create_output_panel(html){
    var output = new Ext.Panel({
        width: 200,
        height: 300,
        margins : '3 3 3 3',
        title : 'Output',
        html : html});
    return output;
}

$(document).ready(function(){

    Ext.state.Manager.setProvider(new Ext.state.CookieProvider());
    var store = new Ext.data.JsonStore({
        root : 'registers',
        fields: ['name', {name: 'value', type: 'int'}]
    });

    var output = create_output_panel("");


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
        title: 'Registers'
    });

    var win = new Ext.Window({
        title    : 'Console',
        closable : true,
        closeAction : 'hide',
        autoWidth: true,
        autoHeight: true,
        layout   : 'column',
        items    : [registers, output]
    });

    $('#home').click(function(event){
        event.preventDefault();
        window.location = "/programs/";
    });
    $('#run').click(function(event){
        event.preventDefault();
        var options = {
            url: ("/run/" + program_name + "/"),
            success: function(responseText, statusText) {
                var data = eval("(" + responseText + ")");
                if(data.exception){
                    var ex_msg = data.exception;
                    var ex_lines = data.msg_list;
                    var final_msg = "";
                    for(var i = 0; i < ex_lines.length; i++){
                        final_msg += ex_lines[i] + "<br />";
                    }
                    Ext.MessageBox.show({
                        title: 'Exception',
                        cls: 'black-text',
                        msg: final_msg,
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.ERROR
                    });
                }
                else{
                    var lines = data.output;
                    var htmlString = "";
                    for(var i = 0; i < lines.length; i++){
                        htmlString += lines[i] + "<br />";
                    }
                    store.loadData(data);
                    win.remove(output);
                    output = create_output_panel(htmlString);
                    win.add(output);
                    win.doLayout();
                    win.show(Ext.get('run'));
                }
            }
        };
        $('#code_form').ajaxSubmit(options);
    });
    $('#update').click(function(event){
        event.preventDefault();
        $('#code_form').attr('action', "/update/").submit();
    });
    $('#reset').click(function(event){
        event.preventDefault();
        $('#code_form').attr('action', "/reset/").submit();
    });
});
