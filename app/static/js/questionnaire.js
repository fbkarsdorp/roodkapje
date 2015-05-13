function toForm(question, selected) {
  var form = document.createElement("form");
  form.setAttribute("method", "get");
  form.setAttribute("action", "");
  form.setAttribute("class", "pure-form");
  form.setAttribute("name", question["number"]);
  if (question["qtype"] === "R" || question["qtype"] === "B") {
    var c = 0;
    for (var oi = 0; oi < question["options"].length; oi++) {
      var option = question["options"][oi];
      c++;
      var label = document.createElement("label");
      label.setAttribute("for", question["number"] + "-" + c);
      label.setAttribute("class", "pure-radio");
      label.setAttribute("accesskey", c);
      var field = document.createElement("input");
      field.setAttribute("type", "radio");
      field.setAttribute("value", option);
      field.setAttribute("id", question["number"] + "-" + c);
      field.setAttribute("name", question["number"]);
      if (option === selected) {
          field.checked = true;
      }
      label.appendChild(field);
      span = document.createElement("span");
      span.innerHTML = option;
      label.appendChild(span);
      form.appendChild(label);
    }
  } else {
    var field = document.createElement("input");
    field.setAttribute("type", "text");
    field.setAttribute("name", question["number"]);
    field.setAttribute("class", "pure-input-1");
    if (typeof selected !== 'undefined') {
      field.setAttribute("value", selected);
    }
    form.appendChild(field);
    form.setAttribute("onkeypress", "return event.keyCode != 13;");
  }
  return form;
}

function Questionnaire(storyname, questions) {
  this.storyname = storyname;
  this.questions = questions;
  this.answers = {};
  this.answers['answers'] = {};
  this.skip = {};
  this.lookup = {};
  this.questionPath = [];
  this.currentQuestion = 0;
  this.line = new ProgressBar.Line('#progressbar', {
      color: "rgb(202, 60, 60)",
      strokeWidth: 0.1
  });

  this.progressPerAnswer = 1.0 / this.questions.length;

  for (var i = 0; i < this.questions.length; i++) {
    this.addSkip(this.questions[i]);
    this.lookup[this.questions[i].number] = i;
  }
}

Questionnaire.prototype.addSkip = function(question) {
  this.skip[question.number] = false;
};

Questionnaire.prototype.update = function(question, value) {
  var queue = [];
  for (var i = 0; i < question.skip.length; i++) {
    queue.push(question.skip[i]);
  }
  while (queue.length > 0) {
    var toskip = queue.shift();
    this.skip[toskip] = value;
    var skip_question = this.questions[this.lookup[toskip]];
    for (var i = 0; i < skip_question.skip.length; i++) {
      queue.push(skip_question.skip[i]);
    }
  }
};

Questionnaire.prototype.next = function() {
  for (var i = this.currentQuestion + 1; i < this.questions.length; i++) {
    if (this.skip[this.questions[i].number] === false) {
      this.currentQuestion = i;
      return true;
    }
  }
  return false;
};

// update the page contents with the given question
Questionnaire.prototype.update_page = function(question) {
  this.line.animate(this.currentQuestion * this.progressPerAnswer);
  $("#description").html(question.question);
  $("#question-form").html(toForm(question, this.answers['answers'][question.number]));
  $("#questioncount").html(this.currentQuestion + 1);
};

Questionnaire.prototype.pop = function() {
  var question = this.questions[this.lookup[this.questionPath.pop()]];
  this.currentQuestion = this.lookup[question.number];
  return question;
};

Questionnaire.prototype.fill_blanks = function() {
  for (var i = 0; i < this.questions.length; i++) {
    var question = this.questions[i];
    if (this.skip[question.number] == true) {
      this.answers['answers'][question.number] = question.default[0];
    }
  }
};

Questionnaire.prototype.current = function() {
  return this.questions[this.currentQuestion];
};

function previous_question(questionnaire) {
  if (questionnaire.questionPath.length === 0 || questionnaire.currentQuestion === 0) {
    return false;
  } else {
    // get the last question on the path
    question = questionnaire.pop();
    // reset the skipped questions.
    questionnaire.update(question, false);
    // update the page
    questionnaire.update_page(question);
  }
  return false;
}

function next_question(questionnaire) {
  // get the current question
  question = questionnaire.current();
  // get the data from the form
  var data = $('.pure-form').serializeArray()[0];
  // check if some answer has been given
  if (typeof(data) == 'undefined' || data.value == null || data.value == "") {
    if (confirm("Weet je zeker dat je geen antwoord kunt geven?") == false) {
      return false;
    } else {
      var data = {};
      data.name = question.number;
      data.value = "NO ANSWER PROVIDED";
    }
  }
  questionnaire.questionPath.push(question.number);
  questionnaire.answers['answers'][data.name] = data.value;

  for (var qi = 0; qi < question.default.length; qi++) {
    if (data.value === question.default[qi]) {
      questionnaire.update(question, true);
      break;
    }
  }
  if (questionnaire.next()) {
    questionnaire.update_page(questionnaire.current());
    return false;
  } else {
    questionnaire.line.animate(1.0);
    // first update the answers object with default answers
    questionnaire.fill_blanks();
    // add the possibly updated story contents
    questionnaire.answers['story'] = $('textarea').val();
    // perform the request
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: questionnaire.storyname,
      data: JSON.stringify(questionnaire.answers),
      type: 'POST',
      dataType: 'json',
      success: function (r) {
        console.log(r);
        $("#questionaire").html("");
        var button = document.createElement("button");
        button.setAttribute("type", "submit");
        button.setAttribute("class", "button-next pure-u-1 pure-button");
        button.setAttribute("onclick", "window.location='/'");
        button.innerHTML = "Volgende verhaal";
        div = document.getElementById("questionaire");
        div.appendChild(button);
      }
    });
    return true;
  }
}

$(document).ready(function() {

  var questionnaire = new Questionnaire(storyname, questions);

  question = questionnaire.current()
  questionnaire.questionPath.push(question.number);
  questionnaire.update_page(question);

  $("#previous").click(function() {
    previous_question(questionnaire);
  });

  $("#next").click(function () {
    next_question(questionnaire);
  });

  document.onkeydown = function(e) {
    switch (e.keyCode) {
        case 37:
          previous_question(questionnaire);
          break;
        case 39:
          next_question(questionnaire);
          break;
    }
};

});