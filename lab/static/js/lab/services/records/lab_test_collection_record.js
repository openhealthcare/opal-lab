angular.module('opal.records').factory('LabTestCollectionRecord', function($rootScope, $q, Referencedata, Metadata){
    return function(record, attrs){
      record.formController = "LabTestCollectionFormCtrl";
      Metadata.then(function(metadata){
          if(record.collection_name){
            var columnName = metadata.test_collections[record.collection_name].name;
            record.displayUrl = "/templates/record/" + columnName + ".html";
            record.columnName = columnName;
            record.initialise(attrs);
          }
      });
    };
});
