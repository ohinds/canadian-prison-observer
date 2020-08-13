from flask import Flask
app = Flask(__name__)

html = """
<html>
<head>
<title>
Canada Prison Initiative - The Whole Pie, Canada
</title>
</head>
<body>
<div id="observablehq-80b000b4"></div>
<script type="module">
import {Runtime, Inspector} from "https://cdn.jsdelivr.net/npm/@observablehq/runtime@4/dist/runtime.js";
import define from "https://api.observablehq.com/@observablehq/downloading-and-embedding-notebooks.js?v=3";
const inspect = Inspector.into("#observablehq-80b000b4");
(new Runtime).module(define, name => name === "graphic" ? inspect() : undefined);
</script>
</body>
</html>
"""


@app.route("/")
def serve():
    return html


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
