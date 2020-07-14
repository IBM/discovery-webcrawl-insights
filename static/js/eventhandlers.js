function removetags(results, index, highlightindex) {
    txt = "";
    if (results["results"][index]["highlight"]["html"] === undefined)
    {
        return txt;
    }
    if ((highlightindex + 1) < results["results"][index]["highlight"]["html"].length) {
        txt = results["results"][index]["highlight"]["html"][highlightindex];
        txt = txt.replace(/<em>/g, "starthighlight")
        txt = txt.replace(/<\/em>/g, "endhighlight")
        txt = txt.replace(/<a/g, "startanchor")
        txt = txt.replace(/<\/a>/g, "endanchor")
        txt = txt.replace(/<[^>]*>/g, '')
        txt = txt.replace(/startanchor/g, "<a")
        txt = txt.replace(/endanchor/g, "</a>")
        txt = txt.replace(/starthighlight/g, "<em>")
        txt = txt.replace(/endhighlight/g, "</em>");
    }
    return txt;
}

function populateResults() {
    res = document.getElementById("results").value;
    passagesElement = document.getElementById("passages");
    matchingElement = document.getElementById("matching");

    if (res == "home") {
        passagesElement.style.display = "none";
        matchingElement.style.display = "none";
        d3.selectAll("svg").remove();
    }
    else {
        matchingElement.style.display = "inline";
        passagesElement.style.display = "none";
        d3.selectAll("svg").remove();
        results = JSON.parse(document.getElementById("results").value);
        for (i = 0; i < 5; i++) {
            populateMatchingContent(results, (i + 1))
        }
        for (i = 0; i < 5; i++) {
            populatePassageContent(results, (i + 1))
        }
    }
}


function changeSection(e) {
    passagesElement = document.getElementById("passages");
    matchingElement = document.getElementById("matching");

    if (e.id == "matchingbutton") {
        passagesElement.style.display = "none";
        matchingElement.style.display = "inline";
    }

    if (e.id == "passagesbutton") {
        passagesElement.style.display = "inline";
        matchingElement.style.display = "none";
        d3.selectAll("svg").remove();
        titleElement = document.getElementById("charttitle");
        titleElement.innerHTML = "";
    }
}



function populateMatchingContent(results, index) {
    if (index < results["results"].length) {
        content = ""
        matchingtitleid = "matching" + index + "title";
        document.getElementById(matchingtitleid).innerHTML = results["results"][index - 1]["extracted_metadata"]["title"];
        matchingcontentid = "matching" + index + "content";
        content = document.getElementById(matchingcontentid).innerHTML = results["results"][index - 1]["text"].substring(0, 500) + "..."
            + '<br/><div><hr></div>'
            + '<br/><div><h6>Document highlights</h6></div>'
            + '<br/><div><hr></div>'
            + '<br/><div>'
            + removetags(results, index, 0)
            + '</div'
            + '<br/><div><hr></div>'
            + '<br/><div>'
            + removetags(results, index, 1)
            + '</div>'
            + '<br/><div><hr></div>'
            + '<br/><div>'
            + removetags(results, index, 2)
            + '</div>'
            + '<br/><div><hr></div>'
            + '<br/><div><a class="alink" href="' + results["results"][index - 1]["metadata"]["source"]["url"] + '">Open Document</a></div>';

    }
}

function populatePassageContent(results, index) {
    if (index < results["results"].length) {
        passageTitleId = "passage" + index + "title";
        passageContentId = "passage" + index + "content";
        document.getElementById(passageTitleId).innerHTML = results["passages"][index - 1]["passage_text"]
            + '<br/><div><hr></div>'
            + '<br/><div><a class="alink" href="' + results["documenturlmap"][results["passages"][index - 1]["document_id"]] + '">Open Document</a></div>';
        document.getElementById(passageContentId).innerHTML = "Passage relevance " + results["passages"][index - 1]["passage_score"];
    }
}