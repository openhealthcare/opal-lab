directives.directive("removeFromArray", function(){
  return {
    restrict: 'A',
    scope: {
        removeFromArray: '=',
        indexToRemove: '@'
    },
    link: function (scope, element, attrs) {
      element.bind("click", function(){
        scope.removeFromArray.splice(scope.indexToRemove, 1);
      });
    }
  };
});
