var raw_data = [];
var stopwords = [];

var data = [];
var init_state = 0;
var init_submit = 0;
var init_line = 0;
var switch_para = 0;
var marked_id = "";
var marked_word = "";
var marked_concept = "";
var prev_marked_concept = "";
var img = '<img src="../static/images/arrow_icon.png" width="20px" height="20px" hspace = 5px/>';
var label_num = [0];
var word_list = [];
var id = 0;
var title = "";
var s_id = "";
var story_num = 0;
var username = "";

function ShowLogin(){
    LoginBox.style.display = 'block';
    example_space.style.visibility="hidden";
    AnnotationSpace.style.visibility="hidden";
}

function Login(){
    username = InputUsername.value;
    if(username == ""){
        alert("User name cannot be empty.");
    }
    else{
        LoginBox.style.display = "none";
        $.ajax({
            type: "GET",
            url: "/init",
            data: {
                'username': username
            },
            dataType: "text",
            success: function (result) {
                console.log("Got Username!");
                example_space.style.visibility="visible";
                AnnotationSpace.style.visibility="visible";
                get_paragraph();
            }
        })
    }
}

function update_color(c) {
    if (c == "pos") {
        return "deepskyblue";
    } else if (c == "neg") {
        return "indianred";
    }
}

function update_color_light(c) {
    if (c == "pos") {
        return "#c2ecff";
    } else if (c == "neg") {
        return "transparent";
    }
}

function get_paragraph(){
    $.ajax({
        type: "GET",
        url: "/new_paragraph",
        data: {
            "id": id,
            "title": title,
            "s_id": s_id,
            "username": username
        },
        dataType: "text",
        success: function (result) {
            //alert("Refresh Successful！");
            //alert(s_id + '_' + id);
            if (result == "No more New Paragraphs"){
                alert("Annotation Finished！");
                clear_content();
                return;
            }
            res = JSON.parse(result);
            title = res["title"];
            s_id = res["s_id"];
            id = res["id"];
            raw_data = res['words'];
            switch_para = 1;
            //StoryTitle.innerHTML = "This paragraph is taken from story: " + title.replaceAll('-', ' ') + "<br />"
            StoryTitle.innerHTML = title.replaceAll('-', ' ');
            marked_id = "";
            render_original();
            clear_content();
            switch_para = 0;
            story_num += 1;
            label_num[story_num] = 0;
            word_list[story_num] = "";
            console.log("new paragraph added")
            folder_section();
        }
    })
}

function render_original() {
    data = [];
    console.log(raw_data); 
    /*raw_data.forEach(function (e, i) {
        data.push({
            id: i,
            word: e,
            marked: 0
        })
    })*/
    data = raw_data;
    console.log(data); 
    let paragraph = document.createElement("div");
    paragraph.className = "paragraph";
    paragraph.innerHTML = "";
    data.forEach(function (e) {
        if(e.stop == 0){
            paragraph.innerHTML += `
                <div id="s${e.id}" class="sentence" onclick="update_select('${e.id}', 'pos')">
                    ${e.word}</div>`
        }
        else{
            paragraph.innerHTML += `
                <div id="s${e.id}" class="sentence_no_choose" >
                    ${e.word}
                </div>`
        }
    })
    console.log("new paragraph")
    if(text_space.childNodes.length==0){
        text_space.appendChild(paragraph);
    }
    else{
        text_space.replaceChild(paragraph, text_space.childNodes[0]);
    }
    if(init_line == 0){
        init_line = 1;
    }
    SelectWordInst.style.display = "block";
    //SelectWordInst.innerHTML = "Select a <p1>word</p1> to start."
    SelectWordInst.innerHTML = "<p>Start by selecting a <p1>word</p1> that you think is BENEFICIAL for <p2>children's education</p2>.</p>"
    SelectWordInst.innerHTML += "<br><br><br><p3>*This annotation task is to create QA pairs beneficial for children's education, with the help of external knowledge from ConceptNet.</p3>"
}

function update_select(d, c) {
    if(init_submit == 1){
        init_state = 0;
    }
    if(data[Number(d)]['marked'] == 1){
        return;
    }
    let selected = document.getElementById("s" + d);
    selected.style.background = "#ffa5a5";
    //selected.style.width = "1px";
    if (c == 'pos') {
        console.log(marked_id, d);
        if(marked_id != ""){
            /*marked new word*/
            prev_marked_concept = "";
            if (data[Number(marked_id)]['marked'] == 0){
                /*marked new word*/
                if(marked_id != d){
                    /*Restore the original background color*/ 
                    document.getElementById("s" + marked_id).style.background = "#DCDCDC";
                }/*update new bg color*/
                else{
                    selected.style.background = "#ffa5a5";
                }
            }/*marked old word*/
            else{
                document.getElementById("s" + marked_id).style.background = "#a9a7ff";
                if (marked_id == d){
                    marked_word = data[Number(d)].word;
                    marked_id = d;
                    return;
                }
            }
        }
        marked_word = data[Number(d)].word;
        add_concept(marked_word);
        marked_id = d;
    }
}

function add_concept(w) {
    $.ajax({
        type: "GET",
        url: "/search",
        data: {
            "word": JSON.stringify(w),
            "username": username
        },
        dataType: "text",
        success: function (result) {
            document.getElementById("submit").style.display = "block";
            write_meaning(result, w);
        }
    })
}

function show_qa() {
    SelectTripleInst.style.display = "none";
    pair.style.display = "block";
    submit.style.display = "block";
    CreateQAInst.style.display = "block";
    //CreateQAInst.innerHTML = `Now you need to create a Question and Answer for the story based on <p1>the word</p1> <p2>"${marked_word}"</p2> and its <p3>Meaning in Wiktionary</p3> and <p4>the ConceptNet Triple</p4> <p5>you choose</p5>.`
    CreateQAInst.innerHTML = `<p>Now you need to create a Question and Answer for the story based on <p1>the word</p1> <p2>"${marked_word}"</p2>.</p> 
    <p6>· You can use its <p3>meaning in Wiktionary</p3>.</p6><br>
    <p6>· Preferrably including <p2>"${marked_word}"</p2> and its <p5>relationship</p5> in the question that can be answered by the <p4>related concept</p4>.</p6><br>
    <p6>· The QA-pair should be beneficial for children's education.</p6>`
    document.getElementById("question").value = "";
    document.getElementById("answer").value = "";
    var qa_div = document.getElementById("QA");
    qa_div.style.display = "block";
    document.getElementById("submit")._tippy.show();
    document.styleSheets[0].insertRule(
        `@keyframes slide-down{
            0%{transform:translateY(100%);}
            100%{transform:translateY(0px);}
          }`
    )
    qa_div.style.animation = "slide-down 0.3s ease-in-out"
}

function write_meaning(data, word) {
    SelectWordInst.style.display = "none";
    CreateQAInst.style.display = "none";
    QA.style.display = "none";
    concept_space.style.display = "block";
    SelectTripleInst.style.display = "block";
    res = JSON.parse(data);
    meaning = res["meaning"].substring(res["triples"][0][0].length + 1).split(";");
    tab_space = "&nbsp;&nbsp;&nbsp;&nbsp;";
    meaning_str = res["triples"][0][0] + ": <br>" + tab_space;
    
    for(let i = 0; i < meaning.length; i++){
        if(i != 0){
            meaning_str += ';<br>' + tab_space;
        }
        meaning_str += meaning[i];
    }

    knowledge_list = res["triples"];
    console.log(typeof(knowledge_list), knowledge_list);
    if(typeof(meaning) == "undefined" || meaning == '' || knowledge_list.length == 0){
        console.log("no knowledge");
        clear_content();
        NoKnowledge.style.display = "block";
        NoKnowledge.innerHTML = "<p1>Please choose a more common word!</p1>";
        SelectTripleInst.style.display = "none";
        return;
    }
    NoKnowledge.style.display = "none";
    var t_string = '<table onclick="show_qa()">';
    t_string += '<tr><td class="table_content" width="30px"></td><td class="table_content" width="100px">Concept</td><td class="table_rel">Relationship</td><td class="table_relcon">Related concept</td></tr>';
    console.log(knowledge_list.length);
    for (let i = 0; i < knowledge_list.length; i++) {
        entity = knowledge_list[i];
        var text = "";
        t_string += `<tr id="tr_${i}" onclick="get_row('tr_${i}')"><td width="30px"><input type="radio" id="radio_${i}" name="TripleSelected" value="tr_${i}"></td>`;
        for (let j = 0; j < entity.length-1; j++) {
            if(j != 0){
                t_string += '<td width="300px">' + entity[j].replaceAll("_", " ") + '</td>'
            }
            else{
                t_string += '<td width="100px"><p1 style="background-color: #FFA5A5">' + entity[j] + '</p1></td>'
            }
            text += entity[j].toString() + ' ';
        }
        t_string += '</tr>';
    }
    t_string += '</table>'
    
    AboveMeaning.innerHTML = "<p id='MeaningIns'>Meaning of '" + word + "' in Wiktionary:</p>";
    ShowMeaning.innerHTML = meaning_str;
    AboveTriples.innerHTML = "<p id='TripleIns'>Matching triples of '" + word + "' in ConceptNet:</p>";
    ShowTriples.innerHTML = t_string;
    //SelectTripleInst.innerHTML = `Please choose<br>a <p1>triple of "${marked_word}" in ConceptNet</p1><br>from the left box.`
    SelectTripleInst.innerHTML = `<p>Please choose<br>a <p1>triple of <p3>"${marked_word}"</p3> in ConceptNet</p1> that:</p><br><p2>1. provides external knowledge outside the story</p2><br><p2>2. is beneficial for children's education.</p2>`
    /*!!!!new QA display!!!*/
    //document.getElementById("pair").style.display = "block";
    //document.getElementById("submit").style.display = "block";
    //show_qa();
}

function get_row(row_id){
    document.getElementById('radio' + row_id.substring(2)).checked = true;
    document.getElementById(row_id).style.backgroundColor = "#FFE49D";
    if (prev_marked_concept != ""){
        document.getElementById(prev_marked_concept).style.backgroundColor = "white";
    }
    prev_marked_concept = row_id;
    marked_concept = row_id.slice(3);
}

function sub() {
    var q = document.getElementById("question").value;
    var a = document.getElementById("answer").value;
    //var c = marked_concept;
    var c = marked_concept.toString();
    if(marked_id == ""){
        alert("You haven't chose a word!");
        return;
    }
    else if (marked_concept == ""){
        alert("You haven't chose a concept!");
        return;
    }
    if(q.length == 0){
        //alert("You haven't enter your question!");
        document.getElementById("question")._tippy.show();
    }
    if(a.length == 0){
        //alert("You haven't enter your answer!");
        document.getElementById("answer")._tippy.show();
    }
    if(q.length == 0 || a.length == 0){
        return;
    }
    
    console.log(init_state, q, a, c);
    show_submit = 0;
    $.ajax({
        type: "GET",
        url: "/submit",
        data: {
            "question": q,
            "answer": a,
            "concept": c,
            "title": title,
            "section": id,
            'word_id': marked_id,
            "username": username
        },
        dataType: "text",
        success: function () {
            //alert("Submit Successful！");
            init_submit = 1;
            console.log("Done!");
            label_num[story_num] += 1;
            word_list[story_num] += "<p class='words'>" + marked_word + "</p>" //+ word_list[story_num];
            //document.getElementById("label_words").innerHTML = "You have labeled "+ label_num + " words." + word_list;
            //document.getElementById(marked_id).style.borderColor = "deepskyblue";
            let selected = document.getElementById("s" + marked_id);
            selected.style.background = "#a9a7ff";
            data[Number(marked_id)]['marked'] = 1;
            clear_content();
            SelectWordInst.style.display = "block";
            //folder_section();
        }
    })
}

function initial_state(){
    init_state = 1;
    ShowLogin();
    //concept_space.style.display = "none";
}

function clear_content(){
    document.getElementById("question").value = "";
    document.getElementById("answer").value = "";
    //document.getElementById("question").setAttribute("placeholder", "Please enter your question.");
    //document.getElementById("answer").setAttribute("placeholder", "Please enter your answer.");
    /*if (switch_para == 0){
        update_select(marked_id, "neg")
    }*/
    AboveMeaning.innerHTML = "";
    ShowMeaning.innerHTML = "";
    AboveTriples.innerHTML = "";
    ShowTriples.innerHTML = "";
    document.getElementById("pair").style.display = "none";
    document.getElementById("submit").style.display = "none";
    concept_space.style.display = "none";
    QA.style.display = "none";
    //SelectWordInst.style.display = "none";
    SelectTripleInst.style.display = "none";
    CreateQAInst.style.display = "none";
    prev_marked_concept = "";
    //marked_id = "";
    marked_concept = "";
}

tippy('#question', {
    content: "You haven't enter your question!",
    trigger: 'manual',
    theme: 'material'
});

tippy('#answer', {
    content: "You haven't enter your answer!",
    trigger: 'manual',
    theme: 'material'
});

tippy('#submit', {
    content: "Click here to submit your question and answer!",
    trigger: 'manual',
    theme: 'material'
});

tippy('#finish_button', {
    content: "Click here to move on to a new paragraph!",
    trigger: 'mouseenter focus',
    theme: 'material'
})

function folder_section(){
    var fd = document.getElementsByClassName("folder");
    for (let i = 0; i < fd.length; i++){
        fd[i].addEventListener("click", function(){
            this.classList.toggle("active");
            var wordline = this.nextElementSibling;
            if (wordline.style.maxHeight){
                wordline.style.maxHeight = null;
            }else{
                wordline.style.maxHeight = wordline.scrollHeight + "px";
            }
        });
    }
}

//render_original();
initial_state();
folder_section();

