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
    var table = document.getElementById('rank');
    for(var i=0; i<data.length; i++) {
        // var list = document.getElementById(data[i].anchor);
        // var _item = document.createElement('a');
        // _item.href = data[i].num;
        // _item.innerText = data[i].rank ;
        var row = table.insertRow(i+1)
        var c0 = row.insertCell(0);
        var c1 = row.insertCell(1);
        var c2 = row.insertCell(2);
        var c3 = row.insertCell(3);
        var c4 = row.insertCell(4);
        row.insertCell(5); // filler
        var c5 = row.insertCell(6);

        c0.innerText = data[i].num
        c1.innerText = data[i].rank
        c2.innerText = data[i].author
        c3.innerText = data[i].total
        c4.innerText = data[i].recent
        c5.innerText = data[i].affiliation

        // Style
        c0.setAttribute("class", "numerl");
        c1.setAttribute("class", "numerl");
        c3.setAttribute("class", "numero");
        c4.setAttribute("class", "numero");

        // var entry = document.createElement('li');
        // entry.appendChild(_item);
        // entry.appendChild(document.createTextNode(", " + data[i].author + ", " + data[i].total + "."));
        // list.appendChild(entry);
    }
});
