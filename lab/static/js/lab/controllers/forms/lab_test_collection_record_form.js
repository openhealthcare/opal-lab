angular.module('opal.controllers').controller("LabTestCollectionFormCtrl",
  function($scope, $controller, $modalInstance, metadata, referencedata, profile, item, episode){

    var parentCtrl = $controller("EditItemCtrl", {
      $scope: $scope,
      $modalInstance: $modalInstance,
      episode: episode,
      metadata: metadata,
      referencedata: referencedata,
      item: item,
      profile: profile
    });
    $scope.metadata = metadata;
    $scope.referencedata = referencedata;
    $scope.collection_names = _.keys(metadata.test_collections);
    $scope.local = {};

    if(!item.collection_name){
      $scope.$watch("local.collection_name", function(){
          if($scope.local && $scope.local.collection_name && $scope.local.collection_name.length){
            if(metadata.test_collections[$scope.local.collection_name]){
              item.columnName = metadata.test_collections[$scope.local.collection_name].name;
              $scope.editing[item.columnName] = {};
              $scope.editing[item.columnName].collection_name = $scope.local.collection_name;
            }
          }
      });
    }
    else{
      $scope.oldCollection = true;
      var schema = metadata.test_collections[item.collection_name];
      $scope.formUrl = schema.form_url;
    }
  }
);
