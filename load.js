function loadJSON(callback) {
        var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
        xobj.open('GET', './ranking.json', true);
        xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
             callback(xobj.responseText);
          }
        };
        xobj.send(null);
}

loadJSON(function(response) {
    var data = JSON.parse(response);
    for(var i=0; i<data.length; i++) {
        var list = document.getElementById(data[i].anchor);
        var _item = document.createElement('a');
        _item.href = data[i].num;
        _item.innerText = data[i].rank ;
        var entry = document.createElement('li');
        entry.appendChild(_item);
        entry.appendChild(document.createTextNode(", " + data[i].author + ", " + data[i].total + "."));
        list.appendChild(entry);
    }
});