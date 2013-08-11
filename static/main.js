(function() {
    var learnsomesql = require("learnsomesql");
    
    var queryExecutor = learnsomesql.ajaxQueryExecutor("/query");
    
    var options = JSON.parse(document.getElementById("question-json").value);
    
    console.log(options);
    options.element = document.getElementById("question");
    
    learnsomesql.createQuestionWidget(queryExecutor)(options);
})();
