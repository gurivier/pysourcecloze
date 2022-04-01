var cssRule = 'label.cloze, pre.cloze input, ol.cloze input, ol.cloze li{font-size:13px;font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;}ol.cloze{counter-reset: item;margin-left: 0;padding-left: 0;}ol.cloze li{white-space: pre;padding:0;margin:0;padding-left: 0;display: block;margin-left: 3.5em;}ol.cloze li:before{padding:0;margin:0;border-right: solid 1px black;content: counter(item) " ";counter-increment: item;display: inline-block;text-align: right;width: 3em;padding-right: 0.5em;margin-left: -3.5em;margin-right: 1em;height: 22px;}pre.cloze{border-left: solid 1px black; padding-left:1em;}p.instructions{border: solid 1px black; border-radius: 3px; padding: 12px;}';
var styleElement = document.createElement('style');
styleElement.appendChild(document.createTextNode(cssRule));
document.getElementsByTagName('head')[0].appendChild(styleElement);

function setClozeColor(c) {
 [...document.getElementsByTagName('input')].forEach(function(e) {
  if (e.type == 'text')
   e.style.color = c;
 })
}

function SourceCloze(id, sizes) {
 var i = 0;
 [...document.getElementById(id).getElementsByTagName('input')].forEach(function(e) {
  if (e.type == 'text') {
   e.size = sizes[i++];
   e.maxLength = e.size;
   e.style.padding = '0';
   e.style.height = '15px';
   e.style.fontSize = 'inherit';
   e.style.fontWeight = 'inherit';
   e.style.color = 'purple';
   e.style.borderWidth = '0';
   e.style.backgroundColor = '#ced4da';
   e.addEventListener("focus", function() {
    this.style.boxShadow = 'none';
   });
   e.addEventListener("keyup", function() {
    this.style.backgroundColor = (this.value.length == this.size) ? 'inherit' : '#ced4da';
   });
  }
 });
}
