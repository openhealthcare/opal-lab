angular.module('opal.services').service('LabTestRecord', function($window, toMomentFilter){
  return function(item){
    item.formController = "LabTestFormCtrl";
    return item;
  };
});
