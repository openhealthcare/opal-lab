angular.module('opal.services').service('LabTestCollectionRecord', function($window, toMomentFilter){
  return function(item){
    item.formController = "LabTestCollectionFormCtrl";
    return item;
  };
});
