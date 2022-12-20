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
    var limit = (data.length > 100) ? 100 : data.length;
    for(var i=0; i<limit; i++) {

        var row = table.insertRow(i+1)
        var c0 = row.insertCell(0);
        var c1 = row.insertCell(1);
        var c2 = row.insertCell(2);
        var c3 = row.insertCell(3);
        var c4 = row.insertCell(4);
        var c5 = row.insertCell(5);

        c0.innerText = data[i].num
        c1.innerText = data[i].rank
        c2.innerText = data[i].author
        c3.innerText = data[i].total
        c4.innerHTML = String(data[i].recent).concat('&nbsp')
        c5.innerHTML = String('&nbsp').concat(data[i].affiliation)

        // Style
        c0.setAttribute("class", "numer1");
        c1.setAttribute("class", "numer1");
        c3.setAttribute("class", "numer2");
        c4.setAttribute("class", "numer2");
    }
});