class DefaultTypeComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            item: props.item
        }
    }

    render() {
        if (!$.isEmptyObject(this.state.item)) {

            return <div className="form-group">
                <label htmlFor={this.state.item.name}
                       className="col-xs-2 control-label">{this.state.item.verbose_name}</label>
                <div className="col-xs-10">
                    <input type="text" className="form-control"
                           id={this.state.item.name}
                           name={this.state.item.name}
                           value={this.state.item.value}
                           disabled={!this.props.editable}
                           placeholder={this.state.item.verbose_name}/>
                </div>
            </div>
        } else {
            return <div></div>
        }

    }
}

class DateTimeFieldComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            item: props.item
        }
    }

    render() {
        if (!$.isEmptyObject(this.state.item)) {

            return <div className="form-group">
                <label htmlFor={this.state.item.name}
                       className="col-xs-2 control-label">{this.state.item.verbose_name}</label>
                <div className="col-xs-10">
                    <input type="text" className="form-control"
                           id={this.state.item.name}
                           name={this.state.item.name}
                           value={moment.unix(this.state.item.value).format("YYYY/MM/DD HH:mm:ss")}
                           disabled={!this.props.editable}
                           placeholder={this.state.item.verbose_name}/>
                </div>
            </div>
        } else {
            return <div></div>
        }

    }
}
class FileFieldComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            item: props.item
        }
    }

    render() {
        if (!$.isEmptyObject(this.state.item)) {

            return <div className="form-group">
                <label htmlFor={this.state.item.name}
                       className="col-xs-2 control-label">{this.state.item.verbose_name}</label>
                <div className="col-xs-10">
                    <p className="form-control-static"><a href={this.state.item.value}>{this.state.item.value}</a></p>
                </div>
            </div>
        } else {
            return <div></div>
        }

    }
}
class CharFieldComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            item: props.item
        }
    }

    render() {
        if (!$.isEmptyObject(this.state.item)) {

            return <div className="form-group">
                <label htmlFor={this.state.item.name}
                       className="col-xs-2 control-label">{this.state.item.verbose_name}</label>
                <div className="col-xs-10">
                    <input type="text" className="form-control"
                           id={this.state.item.name}
                           name={this.state.item.name}
                           value={this.state.item.value}
                           disabled={!this.props.editable}
                           placeholder={this.state.item.verbose_name}/>
                </div>
            </div>
        } else {
            return <div></div>
        }

    }
}


let typeProcessor = {
    DateTimeField: DateTimeFieldComponent,
    DateField: DateTimeFieldComponent,
    FileField: FileFieldComponent,
    CharField: CharFieldComponent,
};

function renderComponent(type) {
    let com = typeProcessor[type];
    if (com == undefined) {
        return DefaultTypeComponent;
    }
    return com;
}

class Detail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: {},
        };

        // HTTP Services
        this.getData = this.getData.bind(this);
    }

    componentWillMount() {
        this.getData();
    }

    getData() {
        $.ajax({
            url: this.props.data_url,
            method: "GET",
            data: {},
            success: function (data, status, xhr) {
                this.setState({
                    data: data
                })
            }.bind(this)
        })
    }

    render() {
        if (!$.isEmptyObject(this.state.data)) {
            return <div>{
                this.state.data.map(item => {
                    let com = renderComponent(item.type);
                    return React.createElement(com, {item: item, editable: false}, null);
                })}
            </div>
        } else {
            return <div></div>
        }
    }
}

class FormComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            form: {}
        };

        // Event processor
        this.handleSubmit = this.handleSubmit.bind(this);

        // Http Services
        this.getFormData = this.getFormData.bind(this);
        this.postFormData = this.postFormData.bind(this);

    }

    componentWillMount() {
        this.getFormData();
    }

    getFormData() {
        $.ajax({
            url: this.props.form_url,
            method: 'GET',
            success: function (data, status, xhr) {
                this.setState({form: data})
            }.bind(this)
        });
    }

    handleSubmit(event) {
        event.preventDefault();
        let form = event.target;
        let fd = new FormData(form);
        this.postFormData(fd);
    }

    postFormData(fd) {
        $.ajax({
            url: this.props.form_url,
            method: 'post',
            data: fd,
            success: function (data, status, xhr) {
                if (data.status) {
                    window.location.href = data.url;
                } else {
                    alert(data[Object.keys(data)[0]])
                }
            }.bind(this),
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }.bind(this),
            contentType: false,
            processData: false
        })

    }


    render() {
        if (!$.isEmptyObject(this.state.form)) {
            return <form encType="multipart/form-data" className="form-horizontal" onSubmit={this.handleSubmit}>
                <input type="hidden" name="csrfmiddlewaretoken" value={this.props.csrf_token}/>
                {this.state.form.map(item => {
                    let com = renderComponent(item.type);
                    return React.createElement(com, {item: item, editable: true}, null);
                })}
                <div className="form-group">
                    <div className="col-sm-offset-2 col-sm-10">
                        <button type="submit" className="btn btn-default">创建</button>
                    </div>
                </div>
            </form>
        } else {
            return <div></div>
        }

    }
}