from flask import (jsonify,
                   request,
                   Blueprint,
                   current_app,
                   url_for)

import cnr


info_app = Blueprint('info', __name__,)


@info_app.before_request
def pre_request_logging():
    jsonbody = request.get_json(force=True, silent=True)
    values = request.values.to_dict()
    if jsonbody:
        values.update(jsonbody)

    current_app.logger.info("request", extra={
        "remote_addr": request.remote_addr,
        "http_method": request.method,
        "original_url": request.url,
        "path": request.path,
        "data":  values,
        "headers": dict(request.headers.to_list())})


@info_app.route("/")
def index_discovery():
    host = request.url_root
    domain = request.headers['Host']
    return """<html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="cnr-package" content="{domain}/{{name}} {host}/cnr/api/v1/packages/{{name}}/pull">
    </head>
    <body>
    </body>
    </html>""".format(domain=domain, host=host)


@info_app.route("/version")
def version():
    return jsonify({"cnr-api": cnr.__version__})


@info_app.route("/routes")
def routes():
    import urllib
    output = []
    for rule in current_app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    lines = []
    for line in sorted(output):
        lines.append(line)
    return jsonify({"routes": lines})
