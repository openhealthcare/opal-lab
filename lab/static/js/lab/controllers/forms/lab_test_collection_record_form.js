angular.module('opal.controllers').controller('LabTestFormCtrl',
function(
  $scope, $modalInstance, $modal, $controller,
  profile, item, metadata, referencedata, episode,
  LabTestCollectionFormHelper
) {
      "use strict";

      var parentCtrl = $controller("EditItemCtrl", {
          $scope: $scope,
          $modalInstance: $modalInstance,
          episode: episode,
          metadata: metadata,
          referencedata: referencedata,
          item: item,
          profile: profile
      });
      var vm = this;
      _.extend(vm, parentCtrl);

      $scope.editing.lab_test_collection._formHelper = new LabTestFormHelper(
        $scope.editing.lab_test_collection
      );

      $scope.preSave = function(editing){
          $scope.editing.lab_test_collection._formHelper.preSave(editing);
          delete editing.lab_test_collection._formHelper
      };
});
