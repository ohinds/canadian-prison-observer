from flask import Flask
app = Flask(__name__)

html = """
<html>
<head>
<title>
Canadian Prison Observer
</title>
</head>
<body>
<div id="observablehq-829185ef">
  <div class="observablehq-inputs"></div>
  <div class="observablehq-viewof-sunburst"></div>
  <div class="observablehq-type"></div>
</div>
<script type="module">
  import {Runtime, Inspector} from "https://cdn.jsdelivr.net/npm/@observablehq/runtime@4/dist/runtime.js";
  import define from "https://api.observablehq.com/@ohinds/the-whole-pie-canada.js?v=3";
  (new Runtime).module(define, name => {
    if (name === "inputs") return Inspector.into("#observablehq-829185ef .observablehq-inputs")();
    if (name === "viewof sunburst") return Inspector.into("#observablehq-829185ef .observablehq-viewof-sunburst")();
    if (name === "type") return Inspector.into("#observablehq-829185ef .observablehq-type")();
  });
</script>
</body>
</html>
"""


@app.route("/")
def serve():
    return html


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
